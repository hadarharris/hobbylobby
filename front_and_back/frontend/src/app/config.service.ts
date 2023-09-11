import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { AppComponent } from './app.component';


@Injectable({providedIn:'root'})
export class ConfigService {
  constructor(private http: HttpClient) { }
  // updade_user_details(){
  //   console.log("running")
  //   const headers = new HttpHeaders({'myheader':''});
  //   this.http.post<AppComponent>(
  //     'http://localhost:8080/updatedetails',{'firstname':'alex'}
  //   ).subscribe((res)=>{
  //     console.log(res)
  //   });
  // }
  
}