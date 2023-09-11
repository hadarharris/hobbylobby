import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin } from 'rxjs';
import { User } from 'src/app/shared/models/user';
import { map, max, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8080/api';

  constructor(private http: HttpClient) {}

  fetchClusterUsers(currentUserNum: string): Observable<any> {
    const url = `${this.baseUrl}/fetch_cluster_users/${currentUserNum}`;
    return this.http.get<any>(url).pipe(
      tap(response => {
        console.log('Cluster Users Response:', response);
      })
    );
  }

  fetchAllUsers(currentUserNum: string):Observable<any> {
    const url = `${this.baseUrl}/fetch_all_users/${currentUserNum}`;
    return this.http.get<any>(url).pipe(
      tap(response => {
        console.log('All Users Response:', response);
      })
    );
  }

  searchByExactHobby(currentUserNum: string, queryString: string): Observable<any> {
    const url = `${this.baseUrl}/searchByExactHobby/${currentUserNum}/${queryString}`;
    console.log("searchByExactHobby---", url);
    return this.http.get<any>(url).pipe(
      tap((response) => {
        console.log('Exact Hobby Search Response:', response);
      })
    );
  }
  
  searchByOrHobby(currentUserNum: string, queryString: string): Observable<any> {
    const url = `${this.baseUrl}/searchByOrHobby/${currentUserNum}/${queryString}`;
    console.log("searchByOrHobby---", url);
    return this.http.get<any>(url).pipe(
      tap((response) => {
        console.log('OR Hobby Search Response:', response);
      })
    );
  }
  
  fetchFriends(currentUserNum: string): Observable<any> {
    const url = `${this.baseUrl}/getFriends/${currentUserNum}`;
    return this.http.get<any>(url).pipe(
      tap(response => {
        console.log('Get Friends Response:', response);
      })
    );
  }

  addFriend(currentUserNum: string,friendUserNum: string): Observable<any> {
    const url = `${this.baseUrl}/addFriend/${currentUserNum}/${friendUserNum}`;
    return this.http.get<any>(url).pipe(
      tap(response => {
        console.log('Add Friend Response:', response);
      })
    );
  }

  removeFriend(currentUserNum: string,friendUserNum: string): Observable<any> {
    const url = `${this.baseUrl}/removeFriend/${currentUserNum}/${friendUserNum}`;
    return this.http.get<any>(url).pipe(
      tap(response => {
        console.log('Remove Friend Response:', response);
      })
    );
  }

  checkFriend(currentUserNum: string,friendUserNum: string): Observable<any> {
    const url = `${this.baseUrl}/checkFriend/${currentUserNum}/${friendUserNum}`;
    return this.http.get<any>(url).pipe(
      tap(response => {
        //console.log('check Friend Response:', response);
      })
    );
  }

  //filtering google distance api
  calculateDistance(userCity: string, users:User[],maxDistance:number):Observable<User[]>{
    const observables: Observable<any>[] = [];
    users.forEach(user => {
      const distanceObservable = this.http.get(`${this.baseUrl}/distance/${userCity}/${user.city}`);
      observables.push(distanceObservable);
    });
    return forkJoin(observables).pipe(
      map((results: any[]) => {
        const filtered: User[] = [];
        results.forEach((data: any, index: number) => {
          if (Number(data.distance) <= maxDistance) {
            filtered.push(users[index]);
          }
        });
        return filtered;
      })
    );
  }
  //filtering google distance api
}
