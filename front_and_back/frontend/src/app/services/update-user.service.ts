import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class UpdateUserService {
  

  constructor(private http:HttpClient) { }

  updateUserPost(data: any) {
    console.log("data is "+ data);
    return this.http.post('http://localhost:8080/profile', data);
  }
}
