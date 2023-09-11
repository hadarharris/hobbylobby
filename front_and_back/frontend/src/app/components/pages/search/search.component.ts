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
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit {
  currentUserNum: number = 0;
  curUsers:User[]=[];
  user!: User; // User object to store user information
  query='';
  loading = false;
  errorMessage = "";
  searchMethod: string = 'exact'; // Default to 'exact' search
  private hobby: Hobby = new Hobby();

  constructor(private userService: UserService, private route: ActivatedRoute, private apiService: ApiService,
    private router:Router) {
      if(localStorage.getItem(USER_KEY)){
        let u:any=localStorage.getItem(USER_DETAILS)
        this.user=JSON.parse(u)
      }else{
        this.router.navigateByUrl('/login');
      }
      console.log(this.user)
    }

  ngOnInit(): void {
    HeaderComponent.updateHeaderName()
  }

  search(): void {
    this.errorMessage = "";
  
    if (!this.query.trim() || this.query.trim().length < 3) {
      // Handle the case of an empty or too short query (e.g., display a message to the user)
      this.errorMessage =
        "Brevity is the soul of wit, but please do write something a bit longer.";
      return;
    }
  
    this.loading = true;
  
    if (this.searchMethod === 'exact') {
      // Perform exact phrase search
      this.apiService.searchByExactHobby(this.user.usernum, this.query).subscribe(
        (users) => {
          this.curUsers = users;
          console.log(this.curUsers);
          if (this.curUsers.length === 0) {
            this.errorMessage =
              "It seems like your search matched 0 results. Why don't you try searching something else?";
          }
          this.checkFriends();
          this.loading = false;
        },
        (error) => {
          console.error('Error searching users by hobby:', error);
          this.loading = false;
        }
      );
    } else if (this.searchMethod === 'or') {
      // Perform OR logic search
      this.apiService.searchByOrHobby(this.user.usernum, this.query).subscribe(
        (users) => {
          this.curUsers = users;
          console.log(this.curUsers);
          if (this.curUsers.length === 0) {
            this.errorMessage =
              "It seems like your search matched 0 results. Why don't you try searching something else?";
          }
          this.checkFriends();
          this.loading = false;
        },
        (error) => {
          console.error('Error searching users by hobby:', error);
          this.loading = false;
        }
      );
    }
  }

  checkFriends():void{
    this.curUsers.forEach(user => {
      this.apiService.checkFriend(this.user.usernum,user.usernum).subscribe(
        resp => {
          user.isFriend = resp;
        },
        error => {
          console.error('Error checking friend:', error);
        }
      );
    });
  }

  recheckSingleFriend(friend:User):void{
    this.apiService.checkFriend(this.user.usernum,friend.usernum).subscribe(
      resp => {
        friend.isFriend = resp;
      },
      error => {
        console.error('Error checking single friend:', error);
      }
    );
  }
  
  addFriend(friend_usernum:string):void{
    const chosenUser = this.curUsers.find(user => user.usernum === friend_usernum);
    if (chosenUser) {
      chosenUser.isLoading=true;
      this.apiService.addFriend(this.user.usernum,friend_usernum).subscribe(
        resp => {
          console.log(resp);
          this.recheckSingleFriend(chosenUser);
          chosenUser.isLoading=false;
        },
        error => {
          console.error('Error adding friend:', error);
          chosenUser.isLoading=false;
        }
      );
    }
    
  }

  removeFriend(friend_usernum:string):void{
    const chosenUser = this.curUsers.find(user => user.usernum === friend_usernum);
    if (chosenUser) {
      chosenUser.isLoading=true;
      this.apiService.removeFriend(this.user.usernum,friend_usernum).subscribe(
        resp => {
          console.log(resp);
          this.recheckSingleFriend(chosenUser);
          chosenUser.isLoading=false;
        },
        error => {
          console.error('Error removing friend:', error);
          chosenUser.isLoading=false;
        }
      );
    }
  }

  getHobbyImage(user_hobby:string):string{
    return this.hobby.getHobbyImage(user_hobby);
  }
  
}


