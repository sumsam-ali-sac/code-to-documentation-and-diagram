package main

import (
	"fmt"
	"net/http"
)

type Server struct {
	port int
}

func (s *Server) Start() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Hello, World!")
	})
	http.ListenAndServe(fmt.Sprintf(":%d", s.port), nil)
}

func main() {
    server := Server{port: 8080}
    server.Start()
}
