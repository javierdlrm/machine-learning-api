# Transformer

Transformers are used to apply transformations on the model inputs before sending them to the model for making predictions. They run on a built-in Flask server provided by Hopsworks and require a custom python script implementing the following class.

=== "Python"

    ```python
    class Transformer(object):
        def __init__(self):
            """ Initialization code goes here """
            pass

        def preprocess(self, inputs):
            """ Transform the requests inputs here. The object returned by this method will be used as model input to make predictions. """
            return inputs

        def postprocess(self, outputs):
            """ Transform the predictions computed by the model before returning a response """
            return outputs
    ```

The path to this script has to be provided when calling the `create_transformer()`. Find more details in the [Transformer Reference](transformer_api.md).

See examples of transformer scripts in the serving [example notebooks](https://github.com/logicalclocks/hops-examples/blob/master/notebooks/ml/serving).

## Properties

{{trans_properties}}

## Methods

{{trans_methods}}