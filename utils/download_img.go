package main

import (
	"crypto/md5"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
)

// 生产者
type UrlProducter struct {
	UrlChan *chan string
}

// 生产，向chan中添加url
func (p *UrlProducter) Product() {
	for {
		res, _ := http.Post("url", "", strings.NewReader("6666"))
		defer res.Body.Close()

	}

}

// 消费者
type UrlConsumer struct {
	UrlChan *chan string
}

// 消费，消费chan中的url
func (c *UrlConsumer) Consum() {
	url := <-*c.UrlChan
	res, _ := http.Get(url)
	b, _ := ioutil.ReadAll(res.Body)
	name := fmt.Sprintf("%x", md5.Sum(b))
	ioutil.WriteFile(name+".jpg", b, os.ModePerm)
	fmt.Printf("下载成功!")
}

// 更新消费后的url的状态
func (c *UrlConsumer) UpdateUrlStatus(url string) {}

func main() {

	//维护一个指定大小的chan，定时向chan中写入新的img_url，启动指定数量的协程来消费chan中的img_url
	//生产者消费者模式
	//

	UrlChan := make(chan string, 10)
	UrlChan <- "666\n"
	print(<-UrlChan)

}
