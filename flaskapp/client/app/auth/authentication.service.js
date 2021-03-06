/**
 * Authentication service allows HarriGT modules to make calls to endpoints that require a JWT
 */
(function() {
    'use strict';
  
    angular
      .module('app')
      .factory('authService', authService);

    /* @ngInject */
    function authService($http, $log, $localStorage, $rootScope){

        var authVm = this;

        this.isAuthenticated = function(){
            return $localStorage.isAuthenticated || false;  
        }

        return {

            isAuthenticated: authVm.isAuthenticated,

            getUsername: function(){
                if (authVm.isAuthenticated()) {
                    return $localStorage.userProfile.username;
                }else{
                    return null;
                }
            },

            getAuthToken: function(){
                if (authVm.isAuthenticated()) {
                    return $localStorage.userProfile.authentication_token;
                }else{
                    return null;
                }
            },

            register: function(formdata){
                return $http.post('/security/register', formdata)
                    .then(function(response){
                        var result = response.data;

                        $localStorage.isAuthenticated = (result.meta.code == 200);

                        if($localStorage.isAuthenticated) {
                            $localStorage.userProfile = result.response.user;
                            $localStorage.userProfile.username = formdata.email;
                        }

                        //alert subsystems to the fact that we signed in
                        $rootScope.$broadcast('user:loggedIn');

                        return Promise.resolve($localStorage.userProfile);
                    });

            },

            /**
             * Call POST endpoint to log in to API 
             */
            login: function(username, password){

                return $http.post('/security/login', {
                    "email": username,
                    "password": password
                  }).then(function(response){

                    console.log(response);

                    var result = response.data;

                    console.log("butts");

                    console.log(result);

                    $localStorage.isAuthenticated = (result.meta.code == 200);

                    if($localStorage.isAuthenticated) {
                        $localStorage.userProfile = result.response.user;
                        $localStorage.userProfile.username = username;
                    }

                    //alert subsystems to the fact that we signed in
                    $rootScope.$broadcast('user:loggedIn');

                    return $localStorage.isAuthenticated;
                  })
                  .catch(function(response){
                    console.log(response);
                    console.log("Whoopsie");
                    return false;
                  });

            },

            logout: function(){

                return $http.get("/security/logout")
                    .then(function(){
                        delete $localStorage.isAuthenticated;
                        delete $localStorage.userToken;
                        $rootScope.$broadcast('user:loggedOut');
                    });
            }
        };
    }



})();