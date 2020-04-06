## 抖音爬虫



有效期：2020/04/06可用



## 使用方法

#### 需配合工具

- Postman
- Chrome Devtools



#### Step 1:



手机操作步骤：

打开抖音主页 - 分享 - 复制链接 - 发送到电脑



#### Step2:

电脑操作：

点击链接 - 将网址复制后使用浏览器访问



#### Step3:

1. F12打开Devtools
2. 选择手机预览模式
3. 点击作品，找到对应url
4. 点击url，右键 - Copy - Copy as cURL



#### STEP4:

打开POSTMAN操作

1. 点击左上角Import 
2. 选择Paste Raw Text将复制的cURL粘贴进去，点击Import
3. 此时点击Send请求检查是否有效
4. 点击Send键紧邻的右下角code选项进入GENERATE CODE SNIPPETS
5. 选择Python - Requests得到header和url
6. 将headers和url替换到脚本开头的对应代码处即可





