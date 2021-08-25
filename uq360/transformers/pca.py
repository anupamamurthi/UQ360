
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from uq360.transformers.feature_transformer import FeatureTransformer


class PCATransformer(FeatureTransformer):
    def __init__(self, k=2):
        super(PCATransformer, self).__init__()
        self.fit_status = False
        self.pca = PCA(n_components=k)
        self.scaler = StandardScaler()

    @classmethod
    def name(cls):
        return ('pca')

    def fit(self, x, y):
        x_scaled = self.scaler.fit_transform(x)
        self.pca.fit(x_scaled)
        self.fit_status = True

    def transform(self, x, predictions):
        x_scaled = self.scaler.transform(x)
        x_transformed = self.pca.transform(x_scaled)
        return x_transformed

    def save(self, output_location=None):
        self.register_pkl_object(self.scaler, 'scaler')
        self.register_pkl_object(self.pca, 'pca')
        self._save(output_location)

    def load(self, input_location=None):
        self._load(input_location)
        pkl_objs, pkl_names = self.pkl_registry
        scaler_ind = pkl_names.index('scaler')
        pca_ind = pkl_names.index('pca')
        self.scaler = pkl_objs[scaler_ind]
        self.pca = pkl_objs[pca_ind]
        assert type(self.scaler) == StandardScaler
        assert type(self.pca) == PCA
        self.fit_status = True