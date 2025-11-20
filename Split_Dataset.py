import os
import shutil
import random
from tqdm import tqdm

# Caminho base do dataset original
base_dir = "data"

# Caminho do novo dataset dividido
output_dir = "dataset"
os.makedirs(output_dir, exist_ok=True)

# Proporcao de treino e teste
train_ratio = 0.8

# Listar classes
classes = ["com_garimpo", "sem_garimpo"]

for cls in classes:
    class_dir = os.path.join(base_dir, cls)
    images = os.listdir(class_dir)
    random.shuffle(images)
    
    # Calcular divisao
    split_idx = int(len(images) * train_ratio)
    train_imgs = images[:split_idx]
    test_imgs = images[split_idx:]
    
    # Criar diretorios de destino
    train_dir = os.path.join(output_dir, "train", cls)
    test_dir = os.path.join(output_dir, "test", cls)
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    # Copiar imagens de treino
    print(f"Copiando imagens de treino para {cls}...")
    for img in tqdm(train_imgs):
        shutil.copy(os.path.join(class_dir, img), os.path.join(train_dir, img))
    
    # Copiar imagens de teste
    print(f"Copiando imagens de teste para {cls}...")
    for img in tqdm(test_imgs):
        shutil.copy(os.path.join(class_dir, img), os.path.join(test_dir, img))

print("Divisao concluida!")