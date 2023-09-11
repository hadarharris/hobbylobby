import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from 'src/app/services/api.service';
import { User } from 'src/app/shared/models/user';
import { UserService } from 'src/app/services/user.service';
import { HeaderComponent } from '../../partials/header/header.component';
import { Hobby } from 'src/app/shared/models/hobby';

const USER_KEY = 'isLoggedIn'; 
const USER_DETAILS = 'loggedUser'

@Component({
  selector: 'app-friends',
  templateUrl: './friends.component.html',
  styleUrls: ['./friends.component.css']
})
export class FriendsComponent implements OnInit {
  friendsUsers: User[] = [];
  user!: User; // User object to store user information
  loading: boolean = true;
  showNoFriendsMsg:boolean = false;
  private hobby: Hobby = new Hobby();

  constructor(private userService: UserService, private route: ActivatedRoute, private apiService: ApiService,
    private router:Router) {
      if(localStorage.getItem(USER_KEY)){
        let u:any=localStorage.getItem(USER_DETAILS)
        this.user=JSON.parse(u)
      }else{
        this.router.navigateByUrl('/login');
      }
    }

  ngOnInit(): void {
    HeaderComponent.updateHeaderName()
    this.fetchFriends();
  }

  fetchFriends(): void {
    this.loading = true;
    this.apiService.fetchFriends(this.user.usernum).subscribe(
      users => {
        this.friendsUsers = users;
        this.loading = false;
        if (this.friendsUsers.length===0){
          this.showNoFriendsMsg=true;
        }
      },
      error => {
        console.error('Error fetching friends:', error);
        this.loading = false;
      }
    );
  }

  removeFriend(friend_usernum:string):void{
    const chosenUser = this.friendsUsers.find(user => user.usernum === friend_usernum);
    if (chosenUser) {
      chosenUser.isLoading=true;
      this.apiService.removeFriend(this.user.usernum,friend_usernum).subscribe(
        resp => {
          console.log(resp);
          this.apiService.fetchFriends(this.user.usernum).subscribe(
            users => {
              this.friendsUsers = users;
              chosenUser.isLoading = false;
              if (this.friendsUsers.length===0){
                this.showNoFriendsMsg=true;
              }
            },
            error => {
              console.error('Error reloading friends:', error);
              chosenUser.isLoading = false;
            }
          );
        },
        error => {
          console.error('Error removing friend:', error);
        }
      );
    }
  }

  getHobbyImage(user_hobby:string):string{
    return this.hobby.getHobbyImage(user_hobby);
  }
}

