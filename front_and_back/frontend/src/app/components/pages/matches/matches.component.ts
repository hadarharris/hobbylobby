import { Component, OnInit } from '@angular/core';
import { User } from 'src/app/shared/models/user';
import { UserService } from 'src/app/services/user.service';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from 'src/app/services/api.service';
import { HeaderComponent } from '../../partials/header/header.component';
import { Hobby } from 'src/app/shared/models/hobby';

const USER_KEY = 'isLoggedIn'; 
const USER_DETAILS = 'loggedUser'

@Component({
  selector: 'app-matches',
  templateUrl: './matches.component.html',
  styleUrls: ['./matches.component.css']
})
export class MatchesComponent implements OnInit {
  currentUserNum: number = 0;
  clusterUsers: User[] = [];
  user!: User; // User object to store user information
  loading: boolean = true;
  maxDistance:number=0;
  filteredUsers: User[] = [];
  showNoMatchesMsg:boolean = false;
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
    this.fetchClusterUsers()
  }

  fetchClusterUsers(): void {
    this.loading = true;
    this.apiService.fetchClusterUsers(this.user.usernum).subscribe(
      users => {
        this.clusterUsers = users;
        this.filteredUsers = users;
        //console.log(this.clusterUsers);
        this.checkFriends();
        this.loading = false;
        if (this.filteredUsers.length===0){
          this.showNoMatchesMsg=true;
        }
      },
      error => {
        console.error('Error fetching cluster users:', error);
        this.loading = false;
      }
    );
  }

  checkFriends():void{
    this.filteredUsers.forEach(user => {
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
    const chosenUser = this.clusterUsers.find(user => user.usernum === friend_usernum);
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
    const chosenUser = this.clusterUsers.find(user => user.usernum === friend_usernum);
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


  //filtering using google distance api
  filterMatchesByDistance(){
    this.filteredUsers=[];
    this.loading=true;
    this.showNoMatchesMsg=false;
    this.apiService.calculateDistance(this.user.city, this.clusterUsers,this.maxDistance).subscribe(
      users => {
        this.filteredUsers=users;
        this.checkFriends();
        this.loading=false;
        if (this.filteredUsers.length===0){
          this.showNoMatchesMsg=true;
        }
      },error => {
        console.error('Error filtering:', error);
        this.loading=false;
        this.showNoMatchesMsg=true;
      });
  }

  removeFilters(){
    this.showNoMatchesMsg=false;
    this.filteredUsers=this.clusterUsers;
  }
  //filtering google distance api
}


