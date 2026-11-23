import coremltools as ct
import torchvision
import torch

#in order to use this script python 3.11 + torch 2.7.0 needed

model = torchvision.models.resnet18(weights=None)


#weights being loaded into the CPU
model.fc = torch.nn.Linear(model.fc.in_features, 7)
model.load_state_dict(torch.load("mag7_resnet18.pth", map_location="cpu"))
model.eval()


#tracing model with example data
example_input = torch.rand(1, 3, 224, 224)
traced_model = torch.jit.trace(model, example_input)


# alphabetical order matches how ImageFolder sorted the mag7/ subfolders during training
classes = ["Amazon", "Apple", "Google", "Meta", "Microsoft", "Nvidia", "Tesla"]

model_from_trace = ct.convert(
    traced_model,
    inputs=[ct.ImageType(name="image", shape=example_input.shape, scale=1/255.0)],
    classifier_config=ct.ClassifierConfig(classes),
)

model_from_trace.save("mag7.mlpackage")
