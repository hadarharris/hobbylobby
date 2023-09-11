import { Component, OnInit } from '@angular/core';
import { UpdateUserService } from 'src/app/services/update-user.service';
import { CitiesService } from 'src/app/services/cities.service';
import { UserService } from 'src/app/services/user.service';
import { User } from 'src/app/shared/models/user';
import { Router } from '@angular/router';
import { HeaderComponent } from '../../partials/header/header.component';

const USER_KEY = 'isLoggedIn'; 
const USER_DETAILS = 'loggedUser'

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  user!: User; // User object to store user information
  resp:any="";
  cities:string[]=[];
  isEditFormVisible: boolean = false;
  isDetailsVisible:boolean=true;
  loading:boolean = false;
  formattedDateOfBirth: string = '';
  // Declare male and female icon classes
  userProfilePicture: string = '';
  isPasswordEmailFormVisible: boolean = false;
  isOtherDetailsFormVisible: boolean = false;
  success: boolean = false;

  constructor(private userService: UserService,private updateUserService: UpdateUserService,private citiesService:CitiesService,private router:Router) { 
    if(localStorage.getItem(USER_KEY)){
      let u:any=localStorage.getItem(USER_DETAILS)
      this.user=JSON.parse(u)
      this.formattedDateOfBirth = this.convertDateFormat(this.user.date_of_birth);
    }else{
      this.router.navigateByUrl('/login');
    }
    this.updateUserProfilePicture();
  }

  ngOnInit(): void {
    HeaderComponent.updateHeaderName()
    this.getCities();
  }

  updateUserProfilePicture() {
    // Determine the path to the profile picture based on the user's gender
    if (this.user.gender === 'M') {
      this.userProfilePicture = 'assets/images/male.png'; // Path to male profile picture
    } else if (this.user.gender === 'F') {
      this.userProfilePicture = 'assets/images/female.png'; // Path to female profile picture
    }
  }
   

  getUserInfo() {
    this.userService.getUserInfo(this.user.usernum).subscribe(
      (user) => {
        this.user = user; 
        // Assign the received user details to the user property
        console.log('Received user:', this.user); // Debugging line

      },
      (error) => {
        console.error('Error fetching user information:', error);
      }
    );
  }

  convertDateFormat(dateString: string): string {
    const parts = dateString.split('/'); // Split the date string into parts
    if (parts.length === 3) {
      // Ensure there are three parts (month, day, year)
      const year = parts[2];
      const month = parts[0].padStart(2, '0'); // Ensure double-digit month
      const day = parts[1].padStart(2, '0'); // Ensure double-digit day
      return `${year}-${month}-${day}`;
    }
    // Return the original string if it couldn't be parsed
    return dateString;
  }

  
  // Inside a function where you update the user's data (e.g., ngOnInit, getUserInfo, etc.

  getCities(){
    this.citiesService.getCities().subscribe(data => {
      let cur_data = data.toString().replace(/[\[\]"]/g, '');
      this.cities = cur_data.split(",").map(city => city.trim());
    });
    return
  }

  showPasswordEmailForm() {
    this.isPasswordEmailFormVisible = true;
    this.isOtherDetailsFormVisible = false;
    this.isDetailsVisible = false;
  }

  showOtherDetailsForm() {
    this.isPasswordEmailFormVisible = false;
    this.isOtherDetailsFormVisible = true;
    this.isDetailsVisible = false;
  }


  hideForms() {
    this.isPasswordEmailFormVisible = false;
    this.isOtherDetailsFormVisible = false;
    this.isDetailsVisible = true;
    this.resp = "";
    this.success = false;
  }

  updatePasswordEmail() {
    // Logic to update password and email
    this.resp = "";
    console.log('updatePasswordEmail method called'); // Debugging line
    console.log('Usernum in updatePasswordEmail:', this.user.usernum); // Debugging line
    console.log('Fields:', {
      user_mail: this.user.email,
      pwd: this.user.pwd
    });
    if(this.user.email?.trim()=="" || this.user.pwd?.trim()==""){
      this.resp = "at least one field is empty";
      //this.loading = false;
      return;
    }
    if(this.user.email==undefined || this.user.email.length<6 || this.user.email.length>50){
      this.resp = "email address must be at least 6 characters and no more than 50";
      //this.loading = false;
      return;
    }
    if(this.user.email){
      const emailRegex: RegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const res = emailRegex.test(this.user.email);
      if(!res){
        this.resp = "invalid email address";
        //this.loading = false;
        return;
      }
    }
    if(this.user.pwd==undefined || this.user.pwd.trim().length<8 || this.user.pwd.trim().length>14){
      this.resp = "please enter a valid password - 8-14 characters";
      //this.loading = false;
      return;
    }
    // Create an object with the user data to be sent to the server
    const userData = {
      usernum: this.user.usernum,
      email: this.user.email,
      pwd: this.user.pwd,
      which_form: "updatePasswordEmail"
    };
try {
  this.loading = true; // Set loading to true when making the request
  this.updateUserService.updateUserPost({ data: JSON.stringify(userData) }).subscribe((response) => {
    console.log(response);
    this.resp = response;
    // Update local storage only after the updateUserPost request has successfully completed.
    this.userService.getUserInfo(this.user.usernum).subscribe(
      user => {
        localStorage.setItem(USER_DETAILS, JSON.stringify(user));
        this.user = user;
        console.log(this.user);
      },
      error => {
        console.error('Error fetching cluster users:', error);
        this.resp = "Error fetching user information. Please try again later.";
        // Hide the loading indicator in case of an error.
        this.loading = false;
      }
    );
    setTimeout(() => {
      if (this.resp === "successfully updated user") {
        console.log("success on update");
        console.log("this.loading", this.loading);
        this.loading = false; // Hide the loading bar
        this.success = true; // Hide the forms after successful update
      } else {
        console.log("this.loading", this.loading);
        // Handle the case where user addition failed
        this.loading = false; // Hide the loading bar
      }
    }, 1000); // Adjust the delay (in milliseconds) as needed
  });
} catch (error) {
  this.resp = "Something went wrong. Please try again later.";
  console.log("Error on update user: ", error);
} finally {
  // Remove this line as it's unnecessary
  // this.loading = false;
  // this.showEditForm();
}  
  }

  updateOtherDetails() {
    this.resp = "";
    console.log('updateOtherDetails method called'); // Debugging line
    console.log('Usernum in updateOtherDetails:', this.user.usernum); // Debugging line
    console.log('Fields:', {
      firstname: this.user.name,
      surname: this.user.surname,
      gender: this.user.gender,
      city: this.user.city,
      hobbies: this.user.hobby
    });
    if(this.user.name?.trim()=="" || this.user.surname?.trim()=="" || this.user.gender?.trim()=="" || 
    this.user.city?.trim()=="" || this.user.hobby?.trim()==""){
      this.resp = "at least one field is empty";
      //this.loading = false;
      return;
    }
    if(this.user.name==undefined || this.user.name.trim().length<2 || this.user.name.trim().length>20){
      this.resp = "please enter a valid first name";
      //this.loading = false;
      return;
    }
    if(this.user.surname==undefined || this.user.surname.trim().length<2 || this.user.surname.trim().length>30){
      this.resp = "please enter a valid surname";
      //this.loading = false;
      return;
    }
    if(this.user.hobby==undefined || this.user.hobby.trim()=='' || this.user.hobby.trim().length<10){
      this.resp = "writing a more detailed description will help you find more friends";
      //this.loading = false;
      return;
    }
    if(this.user.hobby.trim().length>200){
      this.resp = "you wrote a little bit too much, try to focus your answer";
      //this.loading = false;
      return;
    }
    // Create an object with the user data to be sent to the server
    const userData = {
      usernum: this.user.usernum,
      name: this.user.name,
      surname: this.user.surname,
      date_of_birth: this.user.date_of_birth,
      gender: this.user.gender,
      city: this.user.city,
      hobby: this.user.hobby,
      which_form: "updateOtherDetails"
    };
try {
  this.loading = true; // Set loading to true when making the request
  this.updateUserService.updateUserPost({ data: JSON.stringify(userData) }).subscribe((response) => {
    console.log(response);
    this.resp = response;
    // Update local storage only after the updateUserPost request has successfully completed.
    this.userService.getUserInfo(this.user.usernum).subscribe(
      user => {
        localStorage.setItem(USER_DETAILS, JSON.stringify(user));
        this.user = user;
        console.log(this.user);
      },
      error => {
        console.error('Error fetching cluster users:', error);
        this.resp = "Error fetching user information. Please try again later.";
        // Hide the loading indicator in case of an error.
        this.loading = false;
      }
    );
    setTimeout(() => {
      if (this.resp === "successfully updated user") {
        console.log("success on update");
        console.log("this.loading", this.loading);
        this.loading = false; // Hide the loading bar
        this.success = true;
        this.updateUserProfilePicture();
      } else {
        console.log("this.loading", this.loading);
        // Handle the case where user addition failed
        this.loading = false; // Hide the loading bar
      }
    }, 1000); // Adjust the delay (in milliseconds) as needed
  });
} catch (error) {
  this.resp = "Something went wrong. Please try again later.";
  console.log("Error on update user: ", error);
} finally {
  // Remove this line as it's unnecessary
  // this.loading = false;
  // this.showEditForm();
}
  }

}
