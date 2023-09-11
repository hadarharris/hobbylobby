import { Component, OnInit } from '@angular/core';
import { AdduserService } from 'src/app/services/adduser.service';
import { CitiesService } from 'src/app/services/cities.service';

@Component({
  selector: 'app-add',
  templateUrl: './add.component.html',
  styleUrls: ['./add.component.css']
})
export class AddComponent implements OnInit {
  user_mail?: string;
  pwd:string = "";
  firstname:string = "";
  surname:string = "";
  gender:string = "";
  dob:string = "";
  city:string = "";
  hobbies:string = "";
  resp:any="";
  cities:string[]=[];
  loading = false;
  showForm=true;
  showSuccess=false;
  constructor(private adduserService: AdduserService,private citiesService:CitiesService) {
    
  }

  ngOnInit() {
    this.getCities()
  }

  getCities(){
    this.citiesService.getCities().subscribe(data => {
      let cur_data = data.toString().replace(/[\[\]"]/g, '');
      this.cities = cur_data.split(",").map(city => city.trim());
    });
    return
  }

  addUser(){
    this.resp="";
    console.log(this.loading)
    if(this.user_mail?.trim()=="" || this.pwd?.trim()=="" || this.firstname?.trim()=="" ||
    this.surname?.trim()=="" || this.gender?.trim()=="" || this.city?.trim()=="" ||
    this.hobbies?.trim()==""){
      this.resp = "at least one field is empty";
      return;
    }
    if(this.user_mail==undefined || this.user_mail.length<6 || this.user_mail.length>50){
      this.resp = "email address must be at least 6 characters and no more than 50";
      return;
    }
    if(this.user_mail){
      const emailRegex: RegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const res = emailRegex.test(this.user_mail);
      if(!res){
        this.resp = "invalid email address";
        return;
      }
    }
    if(this.pwd==undefined || this.pwd.trim().length<8 || this.pwd.trim().length>14){
      this.resp = "please enter a valid password - 8-14 characters";
      return;
    }
    //
    if (this.dob==undefined || this.dob.trim() == "") {
      this.resp = "please enter a date";
      return;
    }
    let cur_date:Date=new Date();
    let typedDt:Date=new Date(this.dob);
    let typedAge:number = cur_date.getFullYear()-typedDt.getFullYear()
    if(typedAge < 16 || typedAge > 120){
      this.resp = "you must be at least 16 to register and not older than 120";
      return;
    }
    if(this.firstname==undefined || this.firstname.trim().length<2 || this.firstname.trim().length>20){
      this.resp = "please enter a valid first name";
      return;
    }
    if(this.surname==undefined || this.surname.trim().length<2 || this.surname.trim().length>30){
      this.resp = "please enter a valid surname";
      return;
    }
    if(this.hobbies==undefined || this.hobbies.trim()=='' || this.hobbies.trim().length<3){
      this.resp = "writing a more detailed description will help you find more friends";
      return;
    }
    if(this.hobbies.trim().length>200){
      this.resp = "you wrote a little bit too much, try to focus your answer";
      return;
    }
    this.loading=true;
    this.adduserService.addUserPost({ data: JSON.stringify({email:this.user_mail,pwd:this.pwd,
      firstname:this.firstname,surname:this.surname,gender:this.gender,dob:this.dob,city:this.city,hobbies:this.hobbies}) }).subscribe((response) => {
      console.log(response);
      this.resp=response;
      setTimeout(() => {
        if (this.resp === "success") {
          console.log("success on add");
          this.showForm = false;
          this.showSuccess = true; // Show the success message
          this.loading = false; // Hide the loading bar
          this.resp = "Your account was successfully created. Welcome to the community. Start making friends now!";
        } else {
          // Handle the case where user addition failed
          this.loading = false; // Hide the loading bar
        }
      }, 1000); // Adjust the delay (in milliseconds) as needed
    
    });

  }


}