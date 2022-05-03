# IAM 검색기

[API 문서](https://wesky93.github.io/iam-finder/#/aws/aws-iam-user)

## 로컬 실행 방법
uvicorn을 이용하여 fastapi 서버를 띄울 수 있습니다.
참고로 검사할 계정의 인증 정보를 aws cli 를 이용하여 설정 하거나
환경 변수에 해당 인증키 값을 추가 해야 합니다.

```shell
cd src

# 환경 변수로 인증 정보를 추가 할 경우
export AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
export AWS_DEFAULT_REGION=<AWS_DEFAULT_REGION>

# aws cli로 추가 할 경우
aws configure

uvicorn main:app --port 8000
```

`http://localhost:8000/docs` 에 접속하면 API 문서를 확인 하고 테스트 할 수 있습니다.

## 테스트 방법
pytest로 테스트 코드를 실행 하시면 됩니다.
test에 대한 설정은 `/src/pytest.ini` 파일에서 확인 가능합니다.

```shell
cd src
pytest
```

## K8S 배포 방법
k8s/secret.yaml 파일에 인증키 정보를 채워주세요
secret을 사용하기 보다는 IRSA를 사용 하는 것을 추천 드립니다.

```shell
cd ./k8s

# 생성
kubectl apply -f . --namespace=<namespace>

# 삭제
kubectl delete -f . --namespace=<namespace>
```


