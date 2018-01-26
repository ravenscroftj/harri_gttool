(function() {
  'use strict';

  angular
    .module('app.news', [])
    .constant('defaultTitle', 'List News Articles')
    .controller('NewsController', NewsController);

  /* @ngInject */
  function NewsController($scope, $state, $transitions, defaultTitle, newsService) {
    var newsVm = this;
    $scope.$state = $state;
    newsVm.title = defaultTitle;
    newsVm.selected = {};
    newsVm.total_count = 0;

    newsVm.loadFromState = loadFromState;

    $scope.newsClick = function(articleID){
      $state.go('news.article', {
        articleID: articleID
      });
    };

    $scope.$watch('newsFilter',function(newVal,oldVal){
      //do your code
      if(newVal !== oldVal) {
        $state.go('.', {
          filter: newVal
        }).then(reloadNews());
      }
    });

    $scope.nextPage = function(){
      $state.go('.', {
        page: parseInt($state.params.page)+1
      });
    };

    $scope.hideArticle = function(article) {

      if($scope.hidden){
        console.log('Unhiding article ' + article.id);
          $scope.isHiding[article.id] = true;
          newsService.unhideArticle(article).then(function(response){
            newsVm.loadFromState();
          });
      }else{
        console.log('Hiding article ' + article.id);
          $scope.isHiding[article.id] = true;
          newsService.hideArticle(article).then(function(response){
            newsVm.loadFromState();
          });
      }

    };


    $scope.previousPage = function(){
      $state.go('.', {
        page: parseInt($state.params.page)-1
      });
    };

    $scope.$on('$stateChangeStart', function(){
      console.log("Change of state");
    });

    // When the state changes, the controller will be updated and a search will take place.
    $scope.$on('$stateChangeSuccess', function () {
      newsVm.loadFromState();
    });

    $transitions.onEnter({ to: 'news' }, function(transition) {
      newsVm.loadFromState();
    });


    // Load local variables from the state (the URL of the page).
    function loadFromState() {
      console.log("Load news state")
      $scope.isHiding = {};
      $scope.hidden = $state.current.name == "news.hidden";
      $scope.linked = $state.current.name == "news.linked";
      $scope.newsFilter = $state.params.filter;

      reloadNews();
    }

    function reloadNews(){
      var offset = ($state.params.page-1) * 10;
      $scope.offset = offset;

      $scope.isLoading = true;
      newsService.getNews($scope.hidden, $scope.linked, offset, $scope.newsFilter).then(function(data){
        console.log("Got some news");
        $scope.isLoading = false;
        newsVm.newsArticles = data.articles;
        newsVm.total_count = data.total_count;
        $scope.maxOffset = Math.min(offset+10, newsVm.total_count);
      });
    }

    loadFromState();

  }

})();
