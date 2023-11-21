import torch.optim as optim
import torch.nn as nn

import time

criterion = nn.CrossEntropyLoss()
def package_model_components(model_class,list_of_regularizers):

    model_components = []

    for regularizer in list_of_regularizers:
        model = model_class()
        compiled_regularizer = regularizer(model=model, lambda_reg=10**-2)
        optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

        model_component = {
            "model":model,
            "regularizer":compiled_regularizer,
            "optimizer":optimizer
        }

        model_components.append(model_component)
    
    return model_components

def training_loop(optimizer,inputs,labels,model,regularizer_loss=None) -> "loss":
    # get the inputs
    # zero the parameter gradients
    optimizer.zero_grad()

    # forward + backward + optimize
    outputs = model(inputs)
    loss = criterion(outputs, labels)

    # REGULARIZATION
    loss = regularizer_loss.regularized_all_param(reg_loss_function=loss)

    loss.backward()
    optimizer.step()

    return loss

def calculate_regularizer_metrics(model_components,inputs,labels):

    loss_across_regularizers = []
    latency_across_regularizers = []

    for regularizer_index,regularizer in enumerate(model_components):
        
        #time each training loop to get latency
        start = time.time()
        loss = training_loop(inputs,labels,regularizer)
        end = time.time()

        loss_across_regularizers.append(loss.item())
        latency_across_regularizers.append(end - start)

    return loss_across_regularizers,latency_across_regularizers