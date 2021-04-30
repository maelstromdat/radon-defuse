import { Component, HostListener, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import {MatSnackBar} from '@angular/material/snack-bar';

import { InventoryService } from 'app/core/inventory/inventory.service';
import { AddRepositoryDialogComponent, AddRepositoryDialogData } from './add-repo.component';
import { Repository } from 'app/core/repository/repository.model';
import { speedDialFabAnimations } from 'app/shared/speed-dial-fab.animations';

import { merge, Observable, Subject } from 'rxjs';
import { debounceTime, map, switchMap, takeUntil } from 'rxjs/operators';

/**
 * @title Table with pagination
 */
@Component({
  selector     : 'inventory',
  templateUrl  : './inventory.component.html',
  animations: speedDialFabAnimations
})
export class InventoryComponent implements OnInit {


    /**
     * FABs button
     */
    buttons = [];
    fabTogglerState = 'inactive';

    showItems() {
      this.fabTogglerState = 'active';
      this.buttons = [
        { id: 'id-fab-add-repository', icon: 'add', tooltip: 'Add repository' },
        { id: 'id-fab-collect-repositories', icon: 'library_add', tooltip: 'Collect repositories'},
        { id: 'id-fab-download-repositories', icon: 'download', tooltip: 'Download as CSV'}];
    }

    hideItems() {
      this.fabTogglerState = 'inactive';
      this.buttons = [];
    }

    onToggleFab() {
      this.buttons.length ? this.hideItems() : this.showItems();
    }

    /**
     * List
     */

    repositoriesGithub: Repository[]
    repositoriesGitlab: Repository[]
    filteredRepositoriesGithub: Repository[]
    filteredRepositoriesGitlab: Repository[]

    languages = [{ text: 'All', value: 'all'},
                 { text: 'Ansible', value: 'ansible'},
                 { text: 'Python', value: 'python'},
                 { text: 'Tosca', value: 'tosca'}]

    languageSelected: string = 'all'

    languageChanged(){
      if(this.languageSelected.toLowerCase() === 'all'){
          this.assignCopy();
      }else{
          this.filteredRepositoriesGithub = Object.assign([], this.repositoriesGithub).filter(
             item => item.language.toLowerCase().indexOf(this.languageSelected) > -1
          )
          this.filteredRepositoriesGitlab = Object.assign([], this.repositoriesGitlab).filter(
             item => item.language.toLowerCase().indexOf(this.languageSelected) > -1
          )
      }
    }

    filterItem(value){
      if(!value){
          this.assignCopy();
      } // when nothing has typed
      this.filteredRepositoriesGithub = Object.assign([], this.repositoriesGithub).filter(
         item => item.full_name.toLowerCase().indexOf(value.toLowerCase()) > -1
      )
      this.filteredRepositoriesGitlab = Object.assign([], this.repositoriesGitlab).filter(
         item => item.full_name.toLowerCase().indexOf(value.toLowerCase()) > -1
      )
    }

    assignCopy(){
      this.filteredRepositoriesGithub = Object.assign([], this.repositoriesGithub);
      this.filteredRepositoriesGitlab = Object.assign([], this.repositoriesGitlab);
    }


    constructor(private inventoryService: InventoryService,
                private dialog: MatDialog,
                private snackBar: MatSnackBar) {
        this.repositoriesGithub = []
        this.repositoriesGitlab = []
        this.filteredRepositoriesGithub = []
        this.filteredRepositoriesGitlab = []
    }

    ngOnInit() {
      this.getRepositories();
      this.filteredRepositoriesGithub = this.repositoriesGithub
      this.filteredRepositoriesGitlab = this.repositoriesGitlab
    }

    getRepositories(){
      this.inventoryService.getRepositories()
          .subscribe(repositories => {
            for(let repo of repositories){
              if(repo.url.includes('github.com')){
                this.repositoriesGithub.push(repo)
              }else if(repo.url.includes('gitlab.com')){
                this.repositoriesGitlab.push(repo)
              }
            }
          });
    }


    onDelete(id:string){
        this.inventoryService.delete(id)
          .subscribe(deleted => {
            if(!deleted){
                console.log('TO SHOW ERROR THROUGH MESSAGE')
            }else{

                this.repositoriesGithub.forEach((repo,index)=>{
                    if(repo.id==id) this.repositoriesGithub.splice(index,1);
                });
                this.repositoriesGitlab.forEach((repo,index)=>{
                    if(repo.id==id) this.repositoriesGithub.splice(index,1);
                });

                this.assignCopy()
                this.snackBar.open('Repository deleted!', 'Dismiss');
            }
      });
    }

    trackEmployeeById(index: number, repo: Repository): string { return repo.id; }

    @HostListener('click', ['$event.target.id'])
    clickHandler(id: string) {
        console.log(id)

        if(id === 'id-fab-download-repositories'){
            this.export2csv()
        }else if(id === 'id-fab-add-repository'){
            // Open dialog
            const dialogRef = this.dialog.open(AddRepositoryDialogComponent);
            dialogRef.afterClosed()
                     .subscribe(result => {

                  // TODO show loading bar above list
                  this.inventoryService.addRepository(result.url, result.token)
                      .subscribe(repository => {
                        if(!repository){
                            console.log('TO SHOW ERROR THROUGH MESSAGE')
                        }else{
                            // if github and if gitlab:
                            this.repositoriesGithub = [repository, ...this.repositoriesGithub]; // Prepend repository
                            this.assignCopy()
                            this.snackBar.open('Repository added!', 'Dismiss');
                        }
                  });
                });
        }
    }


    export2csv(){
        const header = Object.keys(this.repositoriesGithub[0]).toString()
        const contentGithub = this.repositoriesGithub.map(item => { return Object.values(item).toString() }).join('\n')
        const contentGitlab = this.repositoriesGitlab.map(item => { return Object.values(item).toString() }).join('\n')
        var hiddenElement = document.createElement('a');
        hiddenElement.href = 'data:attachment/csv,' + encodeURI(header + '\n' + contentGithub + '\n' + contentGitlab);
        hiddenElement.target = '_blank';
        hiddenElement.download = 'repositories.csv';
        hiddenElement.click();
    }

//     foo(){
//         console.log('Clicked on Foo')
//     }
//
//     bar(){
//         console.log('Clicked on Bar')
//     }
}

