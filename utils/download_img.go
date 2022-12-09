package main

import (
	"crypto/md5"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

func main() {

	var url string
	fmt.Printf("请输入一个图片url:")
	fmt.Scanln(&url)
	res, _ := http.Get(url)
	b, _ := ioutil.ReadAll(res.Body)
	name := fmt.Sprintf("%x", md5.Sum(b))
	ioutil.WriteFile(name+".jpg", b, os.ModePerm)
	fmt.Printf("下载成功!")
}
