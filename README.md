# Kubernetes pod using Movidius

## Docker configuration for proxied network

Edit your `.docker/config.json` file and add this configuration:
```json
{
 "proxies":
 {
   "default":
   {
     "httpProxy": "http://my-proxy.example.com",
     "httpsProxy": "http://my-proxy.example.com",
     "noProxy": ""
   }
 }
}
```

## Movidius service Docker image

```bash
docker build --no-cache -t movidius .
docker tag movidius {docker_registry}/movidius:{version}
docker push {docker_registry}/movidius:{version}
sudo docker run -t -i --net=host --privileged -v /dev:/dev {docker_registry}/movidius:{version}
```

It'll create service on port 3117 (on every host's network interfaces). 

## Using client

```bash
python3 ncs_client.py
```

## Startup

```bash
kubectl create -f pod.yml
kubectl describe pod movidius
```

## Logs reading

```bash
kubectl logs movidius
```

# Network conversion for Movidius

```bash
$ mvNCCompile squeezenet1.1.prototxt -w squeezenet1.1.caffemodel -s 12 -o movidius_network
```

# Profiling network for Movidius

```bash
$ mvNCProfile squeezenet1.1.prototxt -w squeezenet1.1.caffemodel -s 12
mvNCProfile v02.00, Copyright @ Movidius Ltd 2016

USB: Transferring Data...
Time to Execute :  43.34  ms
USB: Myriad Execution Finished
Time to Execute :  33.79  ms
USB: Myriad Execution Finished
USB: Myriad Connection Closing.
USB: Myriad Connection Closed.
Network Summary

Detailed Per Layer Profile
                                                   Bandwidth   time
#    Name                                    MFLOPs  (MB/s)    (ms)
===================================================================
0    data                                       0.0 74678.9   0.004
1    conv1                                     44.1   755.5   3.518
2    pool1                                      1.8  1365.5   1.142
3    fire2/squeeze1x1                           6.4   749.4   0.514
4    fire2/expand1x1                            6.4   166.8   0.586
5    fire2/expand3x3                           57.8   489.7   1.797
6    fire3/squeeze1x1                          12.8  1415.1   0.544
7    fire3/expand1x1                            6.4   169.4   0.577
8    fire3/expand3x3                           57.8   494.5   1.780
9    pool3                                      0.9  1310.1   0.584
10   fire4/squeeze1x1                           6.4   612.2   0.326
11   fire4/expand1x1                            6.4   158.3   0.353
12   fire4/expand3x3                           57.8   352.3   1.428
13   fire5/squeeze1x1                          12.8   827.8   0.481
14   fire5/expand1x1                            6.4   155.7   0.359
15   fire5/expand3x3                           57.8   351.6   1.431
16   pool5                                      0.5  1230.5   0.311
17   fire6/squeeze1x1                           4.8   385.8   0.309
18   fire6/expand1x1                            3.6   135.2   0.265
19   fire6/expand3x3                           32.5   314.9   1.026
20   fire7/squeeze1x1                           7.2   541.4   0.330
21   fire7/expand1x1                            3.6   136.6   0.263
22   fire7/expand3x3                           32.5   312.8   1.033
23   fire8/squeeze1x1                           9.6   420.4   0.453
24   fire8/expand1x1                            6.4   133.4   0.417
25   fire8/expand3x3                           57.8   283.1   1.769
26   fire9/squeeze1x1                          12.8   568.8   0.446
27   fire9/expand1x1                            6.4   142.6   0.390
28   fire9/expand3x3                           57.8   300.6   1.666
29   conv10                                   200.7   279.0   4.187
30   pool10                                     0.4   700.8   0.533
31   prob                                       0.0     7.5   0.253
-------------------------------------------------------------------
                       Total inference time                   29.08
-------------------------------------------------------------------
Generating Profile Report 'output_report.html'...
```
