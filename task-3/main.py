import tensorflow as tf
from sklearn.preprocessing import label_binarize
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.applications import VGG16,EfficientNetV2M,ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
from tensorflow.keras.applications.vgg16 import preprocess_input as vgg_preprocess
from tensorflow.keras.applications.efficientnet_v2 import preprocess_input as effv2_preprocess
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import(
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    auc
)

IMG_SIZE = (224, 224)
BATCH_SIZE = 16

train_dir = 'dataset/train'
test_dir = 'dataset/test'
validation_dir = 'dataset/validation'

base_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
base_train_data = base_datagen.flow_from_directory(
    train_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)

class_names = list(base_train_data.class_indices.keys())
num_classes = base_train_data.num_classes

def build_data(preprocess_fn):
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        preprocessing_function=preprocess_fn,
        rotation_range=20,
        zoom_range=0.2,
        horizontal_flip=True
    )
    test_datagen = tf.keras.preprocessing.image.ImageDataGenerator(preprocessing_function=preprocess_fn)

    train_data = train_datagen.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    val_data = test_datagen.flow_from_directory(
        validation_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    test_data = test_datagen.flow_from_directory(
        test_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    return train_data, val_data, test_data

def create_vgg16():
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224,224,3))

    base_model.trainable = False

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model

def create_resnet50():
    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224,224,3))

    base_model.trainable = False

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model

def create_efficientnetv2m():
    base_model = EfficientNetV2M(weights='imagenet', include_top=False, input_shape=(224,224,3))

    base_model.trainable = False

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model

def evaluate_model(model, model_name, test_data):

    test_data.reset()
    predictions = model.predict(test_data, verbose=0)

    y_pred = np.argmax(predictions, axis=1)
    y_true = test_data.classes

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    precision_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
    recall_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)

    print(f"\nModel: {model_name}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Precision Macro: {precision_macro:.4f}")
    print(f"Recall Macro: {recall_macro:.4f}")
    print(f"F1 Macro: {f1_macro:.4f}")

    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))

    conf_matrix = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(12, 10))


    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)

    plt.title('Confusion Matrix - ' + model_name)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()

    y_true_bin = label_binarize(y_true, classes=np.arange(num_classes))
    auc_macro = roc_auc_score(y_true_bin, predictions, multi_class='ovr', average='macro')
    auc_micro = roc_auc_score(y_true_bin, predictions, multi_class='ovr', average='micro')
    print(f"AUC Macro (OvR): {auc_macro:.4f}")
    print(f"AUC Micro (OvR): {auc_micro:.4f}")

    plt.figure(figsize=(10, 8))
    for i, class_name in enumerate(class_names):
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], predictions[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f'{class_name} (AUC={roc_auc:.4f})')

    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC Curve - {model_name} (macro={auc_macro:.4f}, micro={auc_micro:.4f})")

    plt.legend()

    plt.show()
    return {
        "accuracy": accuracy,
        "precision_weighted": precision,
        "recall_weighted": recall,
        "f1_weighted": f1,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        "f1_macro": f1_macro,
        "auc_macro_ovr": auc_macro,
        "auc_micro_ovr": auc_micro
    }

def main():
    results = []

    train_data, val_data, test_data = build_data(vgg_preprocess)
    vgg_model = create_vgg16()
    history_vgg = vgg_model.fit(train_data, validation_data=val_data, epochs=10)
    metrics = evaluate_model(vgg_model, "VGG16", test_data)
    results.append({"model": "VGG16", **metrics})

    train_data, val_data, test_data = build_data(resnet_preprocess)
    resnet_model = create_resnet50()
    history_resnet = resnet_model.fit(train_data, validation_data=val_data, epochs=10)
    metrics = evaluate_model(resnet_model, "ResNet50", test_data)
    results.append({"model": "ResNet50", **metrics})

    train_data, val_data, test_data = build_data(effv2_preprocess)
    efficientnetv2m_model = create_efficientnetv2m()
    history_efficientnetv2m = efficientnetv2m_model.fit(train_data, validation_data=val_data, epochs=10)
    metrics = evaluate_model(efficientnetv2m_model, "EfficientNetV2M", test_data)
    results.append({"model": "EfficientNetV2M", **metrics})

    summary_df = pd.DataFrame(results)
    print("\n=== PODSUMOWANIE MODELI ===")
    print(summary_df.sort_values("f1_macro", ascending=False))
    summary_df.to_csv("results_summary.csv", index=False)


if __name__ == "__main__":
    main()
