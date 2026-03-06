"""Digital Twin Verifier for active model verification."""

import torch
import numpy as np
from sklearn.metrics import confusion_matrix


class DigitalTwinVerifier:
    """Active verification using GAN-generated challenge sets."""
    
    def __init__(self, gan, threshold=-0.10, alpha=1.0, beta=0.2, challenge_samples=500):
        """
        Args:
            gan: GAN generator for challenge sets
            threshold: Verification threshold (0.0 - use penalties for detection)
            alpha: Detection Rate weight (1.0)
            beta: False Positive Rate weight (0.3 - low penalty)
            challenge_samples: Number of challenge samples per verification
        """
        self.gan = gan
        self.threshold = threshold
        self.alpha = alpha
        self.beta = beta
        self.challenge_samples = challenge_samples
        self.client_history = {}  # Track client behavior over rounds
    
    def verify(self, model, device='cpu', global_model=None, client_id=None, challenge_seed=None, round_num=1, data_size=None):
        """
        Verify model using challenge set with gradient-based poisoning detection.
        
        Args:
            round_num: Current FL round (for adaptive tolerance)
            data_size: Client's dataset size (for adaptive threshold)

        Returns:
            dict with score, passed, dr, fpr, consistency
        """
        model.eval()
        model.to(device)
        
        # Generate challenge set
        rng = np.random.default_rng(challenge_seed) if challenge_seed is not None else None
        X_challenge, y_challenge = self.gan.generate_challenge_set(
            n_samples=self.challenge_samples,
            device=device,
            rng=rng
        )
        X_tensor = torch.FloatTensor(X_challenge).to(device)
        
        # Get predictions
        with torch.no_grad():
            outputs = model(X_tensor)
            preds = outputs.argmax(dim=1).cpu().numpy()
            
            # Get prediction confidence for backdoor detection
            probs = torch.softmax(outputs, dim=1)
            confidence = probs.max(dim=1)[0].cpu().numpy()
        
        # Binary classification: 0=benign, 1=attack
        y_binary = (y_challenge > 0).astype(int)
        preds_binary = (preds > 0).astype(int)
        
        # Calculate metrics
        tn, fp, fn, tp = confusion_matrix(y_binary, preds_binary, labels=[0, 1]).ravel()
        
        # Traditional metrics
        dr = tp / (tp + fn) if (tp + fn) > 0 else 0.0  # Sensitivity/Recall/TPR
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0  # False Positive Rate

        # Metrics for imbalanced data
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0  # True Negative Rate

        # F1-score: Harmonic mean of Precision and Recall
        f1_score = 2 * (precision * dr) / (precision + dr) if (precision + dr) > 0 else 0.0

        # Balanced Accuracy: Average of Sensitivity and Specificity
        # Better than regular accuracy for imbalanced datasets
        balanced_acc = (dr + specificity) / 2.0

        # Backdoor detection: Check prediction consistency
        confidence_std = np.std(confidence)
        consistency_penalty = 0.0
        
        if confidence_std > 0.4:
            consistency_penalty = 0.1
        
        # Model poisoning detection: Compare weights with global model
        weight_divergence = 0.0
        integrity_score = 1.0  # Default: assume integrity is good
        weight_divergence_penalty = 0.0

        if global_model is not None:
            weight_divergence = self._compute_weight_divergence(model, global_model, device)

            # Normalize divergence to 0-1 range (0=identical, 1=very different)
            # Typical divergence for benign updates: 0.5-2.0
            # Poisoned updates (scale 10x): 10-20+
            normalized_divergence = min(1.0, weight_divergence / 20.0)
            integrity_score = 1.0 - normalized_divergence

            # Progressive penalty based on divergence severity
            if weight_divergence > 10.0:
                # Severe poisoning (scale 10x+)
                weight_divergence_penalty = 0.85
            elif weight_divergence > 5.0:
                # Moderate poisoning (scale 5x)
                weight_divergence_penalty = 0.6
            elif weight_divergence > 2.5:
                # Mild poisoning or natural drift
                weight_divergence_penalty = 0.3
            else:
                # Normal updates
                weight_divergence_penalty = 0.0

        # Behavioral anomaly detection: Track client consistency over rounds
        behavior_penalty = 0.0
        if client_id is not None:
            if client_id not in self.client_history:
                self.client_history[client_id] = []
            
            self.client_history[client_id].append({'dr': dr, 'fpr': fpr, 'conf_std': confidence_std})
            
            # Check for erratic behavior (high variance in metrics)
            if len(self.client_history[client_id]) >= 3:
                history = self.client_history[client_id]
                fpr_variance = np.var([h['fpr'] for h in history[-3:]])
                if fpr_variance > 0.2:
                    behavior_penalty = 0.15
        
        # HYBRID SCORING: Combine Performance + Integrity
        # F1-score measures model performance on challenge set
        # Integrity score measures weight similarity to global model

        performance_score = f1_score

        # Strategy 1: Weighted combination (70% performance, 30% integrity)
        # Works well when both metrics are meaningful
        hybrid_score = 0.7 * performance_score + 0.3 * integrity_score

        # Strategy 2: For severe poisoning, use minimum (both must be high)
        # Prevents attacks with good performance but bad weights
        if weight_divergence > 10.0:
            # Severe case: require BOTH high performance AND high integrity
            base_score = min(performance_score, integrity_score)
        else:
            # Normal case: use weighted hybrid
            base_score = hybrid_score

        # Apply other penalties
        final_score = base_score - consistency_penalty - behavior_penalty

        # Note: weight_divergence_penalty is NOT added here because it's already
        # reflected in integrity_score. Adding both would double-penalize.

        passed = final_score > self.threshold

        return {
            'score': final_score,
            'passed': passed,
            'dr': dr,
            'fpr': fpr,
            'precision': precision,
            'f1_score': f1_score,
            'balanced_accuracy': balanced_acc,
            'integrity_score': integrity_score,
            'weight_divergence': weight_divergence,
            'confidence_std': confidence_std,
            'threshold_used': self.threshold
        }
    
    def _compute_weight_divergence(self, model, global_model, device):
        """Compute L2 norm of weight difference."""
        divergence = 0.0
        count = 0
        
        for (name, param), (_, global_param) in zip(model.named_parameters(), global_model.named_parameters()):
            if param.requires_grad:
                diff = torch.norm(param.data - global_param.data).item()
                divergence += diff
                count += 1
        
        return divergence / count if count > 0 else 0.0
