import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Hobbies_URL } from '../shared/models/constants/urls';
import { Hobby } from '../shared/models/hobby';

@Injectable({
  providedIn: 'root'
})
export class HobbiesService {

  constructor(private http:HttpClient) { }

  getAll(): Observable<Hobby[]>{
    return this.http.get<Hobby[]>(Hobbies_URL);
  }
}
