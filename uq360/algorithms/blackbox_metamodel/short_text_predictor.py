
import numpy as np

from uq360.algorithms.blackbox_metamodel.predictors.predictor_driver import PredictorDriver
from uq360.algorithms.posthocuq import PostHocUQ
from uq360.utils.utils import UseTransformer
import logging

logger = logging.getLogger(__name__)


class ShortTextPredictorWrapper(PostHocUQ):

    def __init__(self, base_model=None, encoder=None):
        super(ShortTextPredictorWrapper).__init__()

        self.encoder = None
        self.encoder = UseTransformer()
        self.predictor = "text_ensemble"
        calib = 'shift'
        self.driver = PredictorDriver(self.predictor,
                                      base_model=base_model,
                                      pointwise_features=None,
                                      batch_features=None,
                                      blackbox_features=None,
                                      use_whitebox=True,
                                      use_drift_classifier=True,
                                      calibrator=calib)

    def fit(self, x_train, y_train, x_test, y_test, test_predicted_probabilities=None):

        if x_train.dtype.type in [np.str_, np.object_] or x_test.dtype.type in [np.str_, np.object_]:
            logger.info('Training/Testing data contains raw text.')
            logger.info('Using an encoder.... %s', self.encoder)
            logger.info('Shapes before encoding %s %s', x_train.shape, x_test.shape)
            x_train = self.encoder.transform(X=x_train)
            x_test = self.encoder.transform(X=x_test)
            logger.info('Shapes after encoding %s %s', x_train.shape, x_test.shape)
        else:
            logger.info('Incoming data is already encoded')

        logger.info("Fitting a text ensemble predictor......")

        self.driver.fit(x_train, y_train, x_test, y_test, test_predicted_probabilities=test_predicted_probabilities)
        self.fitted = True

    def _process_pretrained_model(self, x, y_hat):
        raise NotImplementedError

    def predict(self, x, return_predictions=False, predicted_probabilities=None):
        if not self.fitted:
            raise Exception("Untrained Predictor: fit() method needs to be called before predicting.")

        if x.dtype.type in [np.str_, np.object_]:
            print('Incoming data contains raw text.')
            print('Using an encoder.... %s', self.encoder)
            print('Shapes before encoding %s', x.shape)
            x_prod = self.encoder.transform(X=x)
            print('Shapes after encoding %s', x_prod.shape)
            predictions = self.driver.predict(x_prod, predicted_probabilities=predicted_probabilities)
        else:
            print('Incoming data is already encoded')
            predictions = self.driver.predict(x, predicted_probabilities=predicted_probabilities)

        output = {'predicted_accuracy': predictions['accuracy'], 'uncertainty': predictions['uncertainty']}
        if 'error' in predictions:
            output['error'] = predictions['error']

        if return_predictions:
            output['predictions_per_datapoint'] = predictions['pointwise_confidences']

        return output