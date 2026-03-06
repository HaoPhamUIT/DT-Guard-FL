"""Asynchronous Federated Learning aggregation."""

import numpy as np
from typing import List, Dict, Optional
from collections import deque
from dtguard.models.ids_model import get_parameters, set_parameters


class AsyncFLServer:
    """Asynchronous FL server with staleness handling."""
    
    def __init__(self, global_model, alpha: float = 0.5, buffer_size: int = 3):
        """
        Args:
            global_model: Global model
            alpha: Staleness decay factor (0-1)
            buffer_size: Number of updates to buffer before aggregation
        """
        self.global_model = global_model
        self.alpha = alpha
        self.buffer_size = buffer_size
        
        self.global_version = 0
        self.update_buffer = deque(maxlen=buffer_size)
        self.client_versions = {}
        
    def compute_staleness_weight(self, client_version: int) -> float:
        """Compute weight based on staleness: w = alpha^(t - tau)"""
        staleness = self.global_version - client_version
        return self.alpha ** staleness
    
    def add_update(self, client_id: int, weights: List[np.ndarray], 
                   client_version: int, shapley_weight: float = 1.0):
        """Add client update to buffer."""
        staleness_weight = self.compute_staleness_weight(client_version)
        combined_weight = staleness_weight * shapley_weight
        
        self.update_buffer.append({
            'client_id': client_id,
            'weights': weights,
            'version': client_version,
            'staleness_weight': staleness_weight,
            'shapley_weight': shapley_weight,
            'combined_weight': combined_weight
        })
        
        self.client_versions[client_id] = self.global_version
    
    def should_aggregate(self) -> bool:
        """Check if buffer is full."""
        return len(self.update_buffer) >= self.buffer_size
    
    def aggregate(self) -> List[np.ndarray]:
        """Aggregate buffered updates with staleness weighting."""
        if not self.update_buffer:
            return get_parameters(self.global_model)
        
        # Normalize weights
        total_weight = sum(u['combined_weight'] for u in self.update_buffer)
        normalized_weights = [u['combined_weight'] / total_weight for u in self.update_buffer]
        
        # Weighted aggregation
        current_global = get_parameters(self.global_model)
        aggregated = []
        
        for layer_idx in range(len(current_global)):
            weighted_sum = sum(
                u['weights'][layer_idx] * w 
                for u, w in zip(self.update_buffer, normalized_weights)
            )
            aggregated.append(weighted_sum)
        
        # Update global model
        set_parameters(self.global_model, aggregated)
        self.global_version += 1
        self.update_buffer.clear()
        
        return aggregated
    
    def get_global_weights(self) -> List[np.ndarray]:
        """Get current global model weights."""
        return get_parameters(self.global_model)
    
    def get_version(self) -> int:
        """Get current global version."""
        return self.global_version


def run_async_federated_learning(
    global_model,
    client_models,
    X_clients,
    y_clients,
    X_test,
    y_test,
    verifier,
    config,
    device='cpu',
    use_shapley=True,
    reputation_system=None,
    alpha=0.5,
    buffer_size=3
):
    """
    Run asynchronous federated learning with DT-Guard.
    
    Args:
        alpha: Staleness decay factor
        buffer_size: Updates to buffer before aggregation
    """
    from dtguard.models import train_model, evaluate_model
    from dtguard.security import apply_attack, calculate_shapley_values, calculate_weighted_shapley
    from dtguard.security import CommitteeSelector
    from dtguard.fl.aggregation import compute_verification_stats

    server = AsyncFLServer(global_model, alpha=alpha, buffer_size=buffer_size)

    metrics = {
        'update': [],
        'loss': [],
        'accuracy': [],
        'malicious_detected': [],
        'shapley_history': [],
        'verification_history': [],
        'verification_stats': [],
        'staleness': []
    }

    malicious_indices = list(range(config.num_clients - config.num_malicious, config.num_clients))

    total_updates = config.num_rounds * config.num_clients
    update_count = 0
    aggregation_count = 0

    print(f"\n=== Asynchronous FL (alpha={alpha}, buffer={buffer_size}) ===")

    for round_num in range(config.num_rounds):
        print(f"\n--- Round {round_num + 1}/{config.num_rounds} ---")

        committee = None
        seeds = None
        if getattr(config, 'use_committee', False):
            committee_size = getattr(config, 'committee_size', 3)
            selector = CommitteeSelector(
                num_clients=config.num_clients,
                committee_size=committee_size,
                reputation_scores=reputation_system.get_all_scores() if reputation_system else None,
                shapley_history=metrics['shapley_history']
            )
            committee = selector.select_committee()
            seeds = selector.committee_seeds(round_num + 1)
            print(f"  Committees: {committee}")

        verification_results = [True] * config.num_clients

        # Simulate async: clients train in sequence but don't wait
        for client_id in range(config.num_clients):
            update_count += 1
            
            # Get current global model (may be updated by other clients)
            client_version = server.get_version()
            model = client_models[client_id]
            set_parameters(model, server.get_global_weights())
            
            # Local training
            avg_loss = train_model(
                model, X_clients[client_id], y_clients[client_id],
                epochs=config.local_epochs,
                batch_size=config.batch_size,
                lr=config.learning_rate,
                device=device
            )
            
            weights = get_parameters(model)
            
            # Apply attack
            is_malicious = client_id in malicious_indices
            if is_malicious:
                attack_type_str = config.attack_type if isinstance(config.attack_type, str) else config.attack_type.value
                weights = apply_attack(weights, attack_type_str, config.attack_scale)
                print(f"  Client {client_id}: Update #{update_count} (MALICIOUS, v{client_version})")
            else:
                print(f"  Client {client_id}: Update #{update_count} (benign, v{client_version})")
            
            # DT Verification
            passed = True
            shapley_weight = 1.0
            
            if verifier is not None:
                set_parameters(model, weights)
                if seeds:
                    scores = []
                    drs = []
                    fprs = []
                    passes = []
                    threshold_used = None
                    for seed in seeds:
                        result = verifier.verify(
                            model, device,
                            global_model=global_model,
                            client_id=client_id,
                            challenge_seed=seed,
                            round_num=round_num + 1,
                            data_size=len(X_clients[client_id])
                        )
                        scores.append(result['score'])
                        drs.append(result['dr'])
                        fprs.append(result['fpr'])
                        passes.append(result['passed'])
                        if threshold_used is None and 'threshold_used' in result:
                            threshold_used = result['threshold_used']  # Same threshold for all seeds
                    mean_score = float(np.mean(scores))
                    mean_dr = float(np.mean(drs))
                    mean_fpr = float(np.mean(fprs))
                    passed = sum(passes) >= (len(passes) // 2 + 1)
                    result = {
                        'score': mean_score,
                        'passed': passed,
                        'dr': mean_dr,
                        'fpr': mean_fpr,
                        'threshold_used': threshold_used  # Include threshold in aggregated result
                    }
                else:
                    result = verifier.verify(
                        model, device,
                        global_model=global_model,
                        client_id=client_id,
                        round_num=round_num + 1,
                        data_size=len(X_clients[client_id])
                    )

                if reputation_system:
                    reputation_system.update(client_id, result['passed'], result['score'])

                passed = result['passed']
                verification_results[client_id] = passed
                status = "✓ PASS" if passed else "✗ FAIL"

                # Debug: Always show threshold
                threshold_val = result.get('threshold_used', verifier.threshold)
                threshold_info = f" (threshold={threshold_val})"

                print(f"    Verification: Score={result['score']:.3f}, DR={result['dr']:.3f}, FPR={result['fpr']:.3f} {status}{threshold_info}")

                metrics['verification_history'].append({
                    'update': update_count,
                    'client_id': client_id,
                    'score': result['score'],
                    'dr': result['dr'],
                    'fpr': result['fpr'],
                    'passed': passed
                })
            
            # Add to buffer if passed
            if passed:
                # Calculate Shapley weight (simplified for async)
                if use_shapley:
                    verified_models = [client_models[client_id]]
                    verified_weights = [weights]
                    shapley_values = calculate_shapley_values(
                        verified_models, verified_weights, X_test, y_test, device, n_samples=5
                    )
                    shapley_weight = shapley_values[0]
                
                server.add_update(client_id, weights, client_version, shapley_weight)
                print(f"    Added to buffer (staleness={server.global_version - client_version}, shapley={shapley_weight:.3f})")
            else:
                print(f"    Rejected (malicious)")
            
            # Aggregate if buffer full
            if server.should_aggregate():
                aggregation_count += 1
                print(f"\n  >>> Aggregation #{aggregation_count} (v{server.global_version} -> v{server.global_version + 1})")
                
                # Show buffer contents
                for u in server.update_buffer:
                    print(f"      Client {u['client_id']}: staleness_w={u['staleness_weight']:.3f}, shapley_w={u['shapley_weight']:.3f}")
                
                server.aggregate()
                
                # Evaluate
                accuracy = evaluate_model(global_model, X_test, y_test, device=device)
                print(f"  Global Accuracy: {accuracy:.4f}")
                
                metrics['update'].append(update_count)
                metrics['accuracy'].append(accuracy)
                metrics['loss'].append(float(avg_loss))

        stats = compute_verification_stats(config.num_clients, malicious_indices, verification_results)
        stats['round'] = round_num + 1
        stats['committee'] = committee if verifier is not None else None
        
        # Add scores for this round
        round_scores = []
        for vh in metrics['verification_history']:
            if vh['update'] > (round_num * config.num_clients) and vh['update'] <= ((round_num + 1) * config.num_clients):
                round_scores.append(vh['score'])
        if round_scores:
            stats['scores'] = round_scores
        
        metrics['verification_stats'].append(stats)
        
        # Track malicious detected per round
        malicious_detected_this_round = sum(1 for i in malicious_indices if not verification_results[i])
        metrics['malicious_detected'].append(malicious_detected_this_round)

    # Final aggregation if buffer not empty
    if len(server.update_buffer) > 0:
        print(f"\n>>> Final Aggregation")
        server.aggregate()
    
    final_accuracy = evaluate_model(global_model, X_test, y_test, device=device)
    print(f"\nFinal Accuracy: {final_accuracy:.4f}")
    metrics['accuracy'].append(final_accuracy)
    
    return metrics
