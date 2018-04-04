(function() {
  'use strict';

  angular
    .module('app')
    .run(appRun);

  /* @ngInject */
  function appRun(routerHelper) {
    console.log("Hello");
    routerHelper.configureStates(getStates(), '/');
  }

  function defineParams(){
    return {
      page: {
        value: '1',
        squash:true
      //  dynamic: true
      },
      filter: {
        value: '',
        squash: true,
        dynamic: true,
      }
    };
  }

  function getStates() {
    return [
      {
        state: 'main',
        config: {
          url: '',
          params: defineParams(),
          abstract: true,
          views:{
            header:{
              templateUrl: '/media/build/header.html',
              controller: 'HeaderCtrl'
            },
          }
        }
      },
      {
        state: 'index',
        config:{
          url: '/?page&filter',
          params: defineParams(),
          views:{
            header:{
              templateUrl: '/media/build/header.html',
              controller: 'HeaderCtrl'
            },
            "container@":{
              templateUrl: '/media/build/news/news.html',
              controller: 'NewsController as newsVm',
            }
          }
        }
      },
      {
        state: 'main.logout',
        config: {
          url:'/auth/logout',
          views:{
            "container@":{
              templateUrl: '/media/build/auth/login.html',
              controller: 'AuthController as authVm',
            }
          },
          params: defineParams()
        }
      },
      {
        state: 'main.register',
        config: {
          url:'/auth/register',
          views:{
            "container@":{
              templateUrl: '/media/build/auth/register.html',
              controller: 'AuthController as authVm',
            }
          },
          params: defineParams()
        }
      },
      {
        state: 'main.login',
        config: {
          url:'/auth/login',
          views:{
            "container@":{
              templateUrl: '/media/build/auth/login.html',
              controller: 'AuthController as authVm',
            }
          },
          params: defineParams()
        }
      },
      {
        state: 'main.news',
        config: {
          url:'/news?page&filter',
          views:{
            "container@":{
              templateUrl: '/media/build/news/news.html',
              controller: 'NewsController as newsVm',
            }
          },
          params: defineParams()
        }
      },
      {
        state: 'main.news.hidden',
        config: {
          url:'/hidden',
          views:{
            "container@":{
              templateUrl: '/media/build/news/news.html',
              controller: 'NewsController as newsVm',
            }
          },
          params: defineParams()
        }
      },
      {
        state: 'main.news.linked',
        config: {
          url:'/linked',
          views:{
            "container@":{
              templateUrl: '/media/build/news/news.html',
              controller: 'NewsController as newsVm',
            }
          },
          params: defineParams()
        }
      },
      {
        state: 'main.news.review',
        config: {
          url:'/review',
          views:{
            "container@":{
              templateUrl: '/media/build/news/news.html',
              controller: 'NewsController as newsVm',
            }
          },
          params: defineParams()
        }
      },
      {
        state: 'main.news.spam',
        config: {
          url:'/spam',
          views:{
            "container@":{
              templateUrl: '/media/build/news/news.html',
              controller: 'NewsController as newsVm',
            }
          },
          params: defineParams()
        }
      },
      {
        state: 'main.news.article',
        config: {
          url:'/{articleID:[0-9]+}',
          views:{
            "container@":{
              templateUrl: '/media/build/article/article.html',
              controller: 'ArticleController as newsVm'
            }
          },
          params: defineParams()
        }
      }
    ];

    console.log("hello");
  }

})();
