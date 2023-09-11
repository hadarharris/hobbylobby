import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from 'src/app/services/user.service';
import { IUserLogin } from 'src/app/shared/interfaces/IUserLogin';


@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit{
  users: IUserLogin[] = [];
  loginForm!:FormGroup;
  isSubmitted = false; // did the user press the submit button or not?
  returnUrl = '';
  email?: string;
  pwd:string = "";
  resp:any="";
  loading:boolean = false;
  constructor(private formBuilder:FormBuilder,
    //private adduserService: AdduserService,
     private userService:UserService,
     private activatedRoute:ActivatedRoute,
     private router:Router){}
  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      email:['',[Validators.required, Validators.email]],
      password:['',Validators.required]
    });

    this.returnUrl = this.activatedRoute.snapshot.queryParams['returnUrl']; //return the lastest value of the activated route.
  }


  get form_controls(){ // so we don't have to write (for example) email.loginForm.controls for each property separately
    return this.loginForm.controls;
  }


  submit(){
    this.resp="";
    this.loading = true;
    this.isSubmitted = true;
    console.log("on submit")
      this.userService.login({ data: JSON.stringify({ email: this.email, pwd: this.pwd }) }).subscribe((user) => {
        this.resp=user;
        this.router.navigateByUrl('/friends');
  }, error => {
    console.log("error logging on submit", error)
    this.loading = false;
    this.resp = "Login failed. Make sure your credentials are correct."
  });
}
}
