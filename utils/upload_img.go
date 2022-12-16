package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
)

// 读取所有图片和视频
func Read_all_img(dir string, img_list *[]string) {
	f, _ := os.Open(dir)
	d, _ := f.ReadDir(0)
	for _, f_obj := range d {
		f_name := f_obj.Name()
		if strings.HasSuffix(f_name, ".pyc") || strings.HasSuffix(f_name, ".mp4") {
			*img_list = append(*img_list, f_name)
		}
		if f_obj.IsDir() {
			Read_all_img(dir+"/"+f_name, img_list)
		}

	}
}

// 上传
func upload(img_list []string) {
	var buf bytes.Buffer
	//转成json
	b, _ := json.Marshal(img_list)
	//写入缓冲区
	buf.WriteString(string(b))
	//上传
	r, _ := http.Post("", "", &buf)
	fmt.Printf("r.Body: %v\n", r.Body)
}

// 读取本地合格的图片，上传到服务器
func main() {
	img_list := make([]string, 100)
	Read_all_img(".", &img_list)
	fmt.Printf("img_list: %v\n", img_list)
	upload(img_list)
}
