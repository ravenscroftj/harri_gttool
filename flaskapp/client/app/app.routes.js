(function() {
  'use strict';

  angular
    .module('app')
    .run(appRun);

  /* @ngInject */
  function appRun(routerHelper) {
    routerHelper.configureStates(getStates(), '/');
  }

  function getStates() {
    return [
      {
        state: 'main',
        config: {
          url: '/',
          templateUrl: '/media/build/news/news.html',
          controller: 'NewsController as newsVm',
          params:{
            page: {
              value: '1',
              squash:true
            },
            filter: {
              value: '',
              squash: true
            }
          }
        }
      },
      {
        state: 'news',
        config: {
          url:'/news?page',
          templateUrl: '/media/build/news/news.html',
          controller: 'NewsController as newsVm',
          params:{
            page: {
              value: '1',
              squash:true
            },
            filter: {
              value: '',
              squash: true
            }
          }
        }
      },
      {
        state: 'news.hidden',
        config: {
          url:'/hidden',
          templateUrl: '/media/build/news/news.html',
          controller: 'NewsController as newsVm',
          params:{
            page: {
              value: '1',
              squash:true
            },
            filter: {
              value: '',
              squash: true
            }
          }
        }
      },
      {
        state: 'news.linked',
        config: {
          url:'/linked',
          templateUrl: '/media/build/news/news.html',
          controller: 'NewsController as newsVm',
          params:{
            page: {
              value: '1',
              squash:true
            },
            filter: {
              value: '',
              squash: true
            }
          }
        }
      },
      {
        state: 'news.article',
        config: {
          url:'/{articleID:[0-9]+}',
          templateUrl: '/media/build/article/article.html',
          controller: 'ArticleController as newsVm'
        }
      },
      {
        state: 'search',
        config: {
          url: '/search',
          templateUrl: '/media/build/search/search.html',
          controller: 'SearchController as searchVm'
        }
      },
      {
        state: 'search.term',
        config: {
          url: '/{term:\\w*}',
          templateUrl: '/media/build/search/search.html',
          controller: 'SearchController as searchVm'
        }
      },
      {
        state: 'chat',
        config: {
          url: '/chat',
          templateUrl: '/media/build/chat/chat.html',
          controller: 'ChatController as chatVm'
        }
      }
    ];
  }

})();
