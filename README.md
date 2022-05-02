# IAM 검색기

[API 문서](https://wesky93.github.io/iam-finder/#/aws/aws-iam-user)

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


