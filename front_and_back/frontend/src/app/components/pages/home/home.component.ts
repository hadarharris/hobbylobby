import { Component, OnInit } from '@angular/core';
import { HobbiesService } from 'src/app/services/hobbies.service';
import { Hobby } from 'src/app/shared/models/hobby';
import { ApiService } from 'src/app/services/api.service';

const USER_KEY = 'isLoggedIn'; 

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit{
  

  
  constructor(private hobbiesService:HobbiesService,private apiService:ApiService){
  }

 ngOnInit():void{

 }


 isUserLoggedIn(): boolean {
  const user = localStorage.getItem(USER_KEY); // Adjust the key according to your storage key
  return !!user; // Convert to boolean; return true if user exists, false if not
}

}

