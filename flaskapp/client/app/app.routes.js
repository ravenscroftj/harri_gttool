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
        squash:true,
        //dynamic: true
      },
      filter: {
        value: '',
        //squash: true,
        dynamic: true,
      }
    };
  }

  function getStates() {
    return [
      {
        state: 'main',
        config: {
          url: '/?page&filter',
          templateUrl: '/media/build/news/news.html',
          controller: 'NewsController as newsVm',
          params: defineParams()
        }
      },
      {
        state: 'news',
        config: {
          url:'/news?page&filter',
          templateUrl: '/media/build/news/news.html',
          controller: 'NewsController as newsVm',
          params: defineParams()
        }
      },
      {
        state: 'news.hidden',
        config: {
          url:'/hidden?page&filter',
          templateUrl: '/media/build/news/news.html',
          controller: 'NewsController as newsVm',
          params: defineParams()
        }
      },
      {
        state: 'news.linked',
        config: {
          url:'/linked?page&filter',
          templateUrl: '/media/build/news/news.html',
          controller: 'NewsController as newsVm',
          params: defineParams()
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

    console.log("hello");
  }

})();
