import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
from y2h_ppi.logger import logger

class PyTorchMLP(nn.Module):
    """Multi-Layer Perceptron for pair interaction prediction."""
    
    def __init__(self, input_dim: int, hidden_dims: list = [256, 128, 64], dropout: float = 0.2):
        super().__init__()
        layers = []
        in_dim = input_dim
        for h_dim in hidden_dims:
            layers.append(nn.Linear(in_dim, h_dim))
            layers.append(nn.BatchNorm1d(h_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            in_dim = h_dim
        layers.append(nn.Linear(in_dim, 1))
        self.net = nn.Sequential(*layers)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = self.net(x)
        return torch.sigmoid(logits)

class SiameseNetwork(nn.Module):
    """Siamese Network with shared protein encoder branches."""
    
    def __init__(self, protein_dim: int, hidden_dim: int = 128, dropout: float = 0.2):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(protein_dim, hidden_dim * 2),
            nn.BatchNorm1d(hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU()
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1)
        )
        
    def forward(self, vec_a: torch.Tensor, vec_b: torch.Tensor) -> torch.Tensor:
        emb_a = self.encoder(vec_a)
        emb_b = self.encoder(vec_b)
        
        sum_emb = emb_a + emb_b
        diff_emb = torch.abs(emb_a - emb_b)
        combined = torch.cat([sum_emb, diff_emb], dim=-1)
        
        logits = self.head(combined)
        return torch.sigmoid(logits)

def train_mlp_model(
    X_train: np.ndarray, y_train: np.ndarray,
    X_val: np.ndarray, y_val: np.ndarray,
    epochs: int = 20, batch_size: int = 64, lr: float = 0.001
) -> PyTorchMLP:
    """Train PyTorch MLP with BCE loss and class weighting."""
    input_dim = X_train.shape[1]
    model = PyTorchMLP(input_dim=input_dim)
    
    pos_count = np.sum(y_train)
    neg_count = len(y_train) - pos_count
    pos_weight = torch.tensor([neg_count / max(1, pos_count)], dtype=torch.float32)
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    
    X_t = torch.tensor(X_train, dtype=torch.float32)
    y_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    
    dataset = torch.utils.data.TensorDataset(X_t, y_t)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    logger.info(f"Training PyTorch MLP for {epochs} epochs...")
    model.train()
    for epoch in range(epochs):
        for batch_x, batch_y in dataloader:
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()
            
    model.eval()
    logger.info("PyTorch MLP training complete.")
    return model
