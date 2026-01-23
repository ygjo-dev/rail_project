import yaml
import os
import sys

def load_config(config_path='config/config.yaml'):
    if not os.path.exists(config_path):
        print(f"오류: 설정 파일 '{config_path}'을(를) 찾을 수 없습니다.")
        print("'config/config.template.yaml' 파일을 'config/config.yaml'로 복사한 뒤 설정을 수정해주세요.")
        sys.exit(1) 

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        print(f"오류: 설정 파일을 읽는 중 문제가 발생했습니다: {e}")
        sys.exit(1)

# 사용 예시
if __name__ == "__main__":
    cfg = load_config()
    print(f"설정 로드 완료. 대상 URI: {cfg['neo4j']['uri']}")