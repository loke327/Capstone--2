from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

# Ground truth labels
y_true = [0,0,0,1,1,0,1,0,1,1]

# Predicted probability scores
y_scores = [0.1,0.2,0.8,0.9,0.7,0.2,0.95,0.3,0.6,0.85]

# Compute ROC
fpr, tpr, thresholds = roc_curve(y_true, y_scores)

# Compute AUC
roc_auc = auc(fpr, tpr)

# Plot ROC Curve
plt.figure()
plt.plot(fpr, tpr, label="ROC Curve (AUC = %0.2f)" % roc_auc)
plt.plot([0,1],[0,1],'--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve for Evidence Tampering Detection")
plt.legend(loc="lower right")
plt.show()