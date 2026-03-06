"""Federated Learning aggregation and orchestration."""

import numpy as np
from typing import List
from dtguard.models.ids_model import get_parameters, set_parameters


def federated_averaging(weights_list: List[List[np.ndarray]]) -> List[np.ndarray]:
    """
    FedAvg: Average model weights from multiple clients.
    
    Args:
        weights_list: List of model weights from each client
    
    Returns:
        Averaged weights
    """
    if not weights_list:
        return []
    
    averaged = []
    for layer_idx in range(len(weights_list[0])):
        layer_weights = [w[layer_idx] for w in weights_list]
        averaged.append(np.mean(layer_weights, axis=0))
    
    return averaged


def weighted_federated_averaging(weights_list: List[List[np.ndarray]], 
                                 shapley_weights: np.ndarray) -> List[np.ndarray]:
    """
    Weighted FedAvg using Shapley values.
    
    Args:
        weights_list: List of model weights from each client
        shapley_weights: Normalized Shapley values (sum to 1)
    
    Returns:
        Weighted averaged weights
    """
    if not weights_list:
        return []
    
    averaged = []
    for layer_idx in range(len(weights_list[0])):
        weighted_sum = sum(
            w[layer_idx] * weight 
            for w, weight in zip(weights_list, shapley_weights)
        )
        averaged.append(weighted_sum)
    
    return averaged


def run_federated_learning(
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
    reputation_system=None
):
    """
    Run federated learning with DT-Guard verification.
    
    Args:
        verifier: DigitalTwinVerifier or None (if None, skip verification)
    """
    from dtguard.models import train_model, evaluate_model
    from dtguard.security import apply_attack, calculate_shapley_values, calculate_weighted_shapley
    from dtguard.security import CommitteeSelector

    metrics = {
        'round': [], 
        'loss': [],
        'accuracy': [], 
        'malicious_detected': [],
        'shapley_history': [],
        'verification_history': [],
        'verification_stats': []
    }

    malicious_indices = list(range(config.num_clients - config.num_malicious, config.num_clients))

    for round_num in range(config.num_rounds):
        print(f"\n--- Round {round_num + 1}/{config.num_rounds} ---")
        
        committee = None
        # Local training
        client_weights = []
        client_losses = []
        for i, model in enumerate(client_models):
            # Load global weights
            set_parameters(model, get_parameters(global_model))
            
            # Train locally
            avg_loss = train_model(
                model, X_clients[i], y_clients[i],
                epochs=config.local_epochs,
                batch_size=config.batch_size,
                lr=config.learning_rate,
                device=device
            )
            client_losses.append(avg_loss)
            
            weights = get_parameters(model)
            
            # Apply attack to malicious client
            if i == config.num_clients - 1:  # Last client is malicious
                attack_type_str = config.attack_type if isinstance(config.attack_type, str) else config.attack_type.value
                weights = apply_attack(weights, attack_type_str, config.attack_scale)
                print(f"  Client {i}: Trained (MALICIOUS)")
            else:
                print(f"  Client {i}: Trained (benign)")
            
            client_weights.append(weights)
        
        # DT Verification (skip if verifier is None)
        if verifier is not None:
            print("\n  Digital Twin Verification:")
            verified_weights = []
            verified_indices = []
            verification_scores = []
            verification_results = []

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
                print(f"  Committee (reputation-based): {committee}")

            for i, (model, weights) in enumerate(zip(client_models, client_weights)):
                set_parameters(model, weights)

                if seeds:
                    scores = []
                    drs = []
                    fprs = []
                    passes = []
                    for seed in seeds:
                        result = verifier.verify(
                            model,
                            device,
                            global_model=global_model,
                            client_id=i,
                            challenge_seed=seed,
                            round_num=round_num + 1,
                            data_size=len(X_clients[i])
                        )
                        scores.append(result['score'])
                        drs.append(result['dr'])
                        fprs.append(result['fpr'])
                        passes.append(result['passed'])

                    mean_score = float(np.mean(scores))
                    mean_dr = float(np.mean(drs))
                    mean_fpr = float(np.mean(fprs))
                    passed = sum(passes) >= (len(passes) // 2 + 1)
                    result = {'score': mean_score, 'passed': passed, 'dr': mean_dr, 'fpr': mean_fpr}
                else:
                    result = verifier.verify(
                        model, device,
                        global_model=global_model,
                        client_id=i,
                        round_num=round_num + 1,
                        data_size=len(X_clients[i])
                    )

                # Update reputation if system exists
                if reputation_system:
                    reputation_system.update(i, result['passed'], result['score'])

                status = "✓ PASS" if result['passed'] else "✗ FAIL"
                print(
                    f"    Client {i}: Score={result['score']:.3f}, DR={result['dr']:.3f}, "
                    f"FPR={result['fpr']:.3f} {status}"
                )

                # Store verification history
                metrics['verification_history'].append({
                    'round': round_num + 1,
                    'client_id': i,
                    'score': result['score'],
                    'dr': result['dr'],
                    'fpr': result['fpr'],
                    'passed': result['passed']
                })

                verification_results.append(result['passed'])

                if result['passed']:
                    verified_weights.append(weights)
                    verified_indices.append(i)
                    verification_scores.append(result['score'])

            malicious_detected = len(client_weights) - len(verified_weights)
            print(f"\n  Filtered: {malicious_detected} malicious client(s)")
        else:
            # No verification - use all clients
            verified_weights = client_weights
            verified_indices = list(range(len(client_weights)))
            verification_scores = [1.0] * len(client_weights)
            verification_results = [True] * len(client_weights)
            malicious_detected = 0

        stats = compute_verification_stats(config.num_clients, malicious_indices, verification_results)
        stats['round'] = round_num + 1
        stats['committee'] = committee if verifier is not None else None
        metrics['verification_stats'].append(stats)

        # Calculate Shapley values for verified clients
        if use_shapley and len(verified_weights) > 0:
            print("\n  Calculating Shapley values...")
            
            # Get verified models
            verified_models = [client_models[i] for i in verified_indices]
            
            # Calculate Shapley
            shapley_values = calculate_shapley_values(
                verified_models, verified_weights, X_test, y_test, device, n_samples=10  # Reduced from 20
            )
            
            # Combine with verification scores
            aggregation_weights = calculate_weighted_shapley(shapley_values, verification_scores)
            
            # Store full Shapley history (including 0 for filtered clients)
            full_shapley = np.zeros(config.num_clients)
            for idx, sv in zip(verified_indices, shapley_values):
                full_shapley[idx] = sv
            metrics['shapley_history'].append(full_shapley)
            
            print("  Shapley values:")
            for idx, sv in zip(verified_indices, shapley_values):
                print(f"    Client {idx}: {sv:.4f}")
            
            # Weighted aggregation
            aggregated = weighted_federated_averaging(verified_weights, aggregation_weights)
        else:
            # Simple averaging
            aggregated = federated_averaging(verified_weights)
            metrics['shapley_history'].append(np.zeros(config.num_clients))
        
        # Update global model
        if verified_weights:
            set_parameters(global_model, aggregated)
        
        # Evaluate
        accuracy = evaluate_model(global_model, X_test, y_test, device=device)
        avg_loss = np.mean([client_losses[i] for i in verified_indices]) if verified_indices else np.mean(client_losses)
        print(f"\n  Global Accuracy: {accuracy:.4f}")
        print(f"  Average Loss: {avg_loss:.4f}")
        
        metrics['round'].append(round_num + 1)
        metrics['loss'].append(float(avg_loss))
        metrics['accuracy'].append(accuracy)
        metrics['malicious_detected'].append(malicious_detected)
    
    return metrics


def compute_verification_stats(num_clients, malicious_indices, verification_results):
    """Compute TP/FP/FN/TN from verification pass/fail outcomes."""
    malicious_set = set(malicious_indices)
    tp = fp = tn = fn = 0
    for client_id in range(num_clients):
        passed = verification_results[client_id]
        is_malicious = client_id in malicious_set
        if is_malicious and not passed:
            tp += 1
        elif is_malicious and passed:
            fn += 1
        elif not is_malicious and not passed:
            fp += 1
        else:
            tn += 1

    detection_rate = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    return {
        'tp': tp,
        'fp': fp,
        'tn': tn,
        'fn': fn,
        'detection_rate': detection_rate,
        'false_positive_rate': false_positive_rate
    }
