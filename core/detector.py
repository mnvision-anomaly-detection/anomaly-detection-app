import numpy as np
from PIL import Image
from utils.image_utils import process_single_image
from tensorflow import keras
from core.deep_svdd import DeepSVDD

class Detector:
    def __init__(self, config):
        # 1) SVDD 파라미터 로드
        data = np.load(config['model']['svdd_params'])
        c_np, R_np = data['c'], data['R']

        # 2) Keras 모델 로드
        keras_model = keras.models.load_model(
            config['model']['svdd_model'], compile=False
        )

        # 3) DeepSVDD 객체 생성 & c, R 할당
        self.model = DeepSVDD(
            keras_model=keras_model,
            input_shape=tuple(config['model']['input_size']),
            objective='one-class',
            nu=config['model'].get('nu', 0.1),
            representation_dim=128
        )
        self.model.c.assign(c_np.astype(np.float32))
        self.model.R.assign(float(R_np))

        # 4) 절대 기준 임계값(threshold)에 best_threshold를 설정해주세요
        self.threshold = float(config['detect']['threshold'])

        # 5) 입력 크기
        self.input_size = tuple(config['model']['input_size'])

    def detect(self, image_path):
        img = Image.open(image_path)
        arr = process_single_image(img, self.input_size)
        arr = np.expand_dims(arr, 0)

        # DeepSVDD.predict → 거리(스코어) 배열
        scores = self.model.predict(arr)
        scores = np.atleast_1d(scores).astype(float)

        results = []
        for score in scores:
            is_anomaly = score >= self.threshold
            results.append({
                'anomaly_score': score,
                'is_anomaly': bool(is_anomaly)
            })
        return results

    def detect_batch(self, paths):
        return [self.detect(p) for p in paths]
