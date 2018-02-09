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

    newsVm.$onInit = function(){
      console.log("init");
      loadFromState();
    }

    $scope.checkSpam = function(){
      newsService.checkSpam($scope.newsArticles)
      .then(function(results){
        var spamidx = {};
        console.log(results);
        for (var i=0; i<results.data.length; i++){
          spamidx[results.data[i].id] = results.data[i].scores;
        }

        console.log($scope.newsArticles);

        for(var i=0; i < $scope.newsArticles.length; i++) {
          $scope.newsArticles[i].spamScore = spamidx[$scope.newsArticles[i].id].spam;
        }
      });
    };

    $scope.filterSpam = function(){
      newsService.filterSpam($scope.newsArticles)
      .then(function(results){
        loadFromState();
      });
    };


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

    $scope.previousPage = function(){
      $state.go('.', {
        page: parseInt($state.params.page)-1
      });
    };

    $scope.hideArticle = function(article) {

      if($scope.hidden){
        console.log('Unhiding article ' + article.id);
          $scope.isHiding[article.id] = true;
          newsService.unhideArticle(article).then(function(response){
            loadFromState();
          });
      }else{
        console.log('Hiding article ' + article.id);
          $scope.isHiding[article.id] = true;
          newsService.hideArticle(article).then(function(response){
            loadFromState();
          });
      }

    };

    $scope.spamArticle = function(article) {

      if($scope.spam){
        console.log('UnSpam article ' + article.id);
          $scope.isHiding[article.id] = true;
          newsService.unspamArticle(article).then(function(response){
            loadFromState();
          });
      }else{
        console.log('Spam article ' + article.id);
          $scope.isHiding[article.id] = true;
          newsService.spamArticle(article).then(function(response){
            loadFromState();
          });
      }

    };



    $transitions.onEnter({}, function(transition, state){
      console.log(state);
    });


    // Load local variables from the state (the URL of the page).
    function loadFromState() {

      $scope.isHiding = {};
      $scope.hidden = $state.current.name == "news.hidden";
      $scope.linked = $state.current.name == "news.linked";
      $scope.spam =  $state.current.name == "news.spam";
      $scope.newsFilter = $state.params.filter;

      if($scope.hidden){
        newsVm.title = "Hidden Articles";
      }else if($scope.linked){
        newsVm.title = "Linked Articles";
      }else if ($scope.spam) {
        newsVm.title = "Spam Articles";
      }

      console.log("Load news state", $state.current.name)

      reloadNews();
    }

    function reloadNews(){
      var offset = ($state.params.page-1) * 10;
      $scope.offset = offset;

      console.log($scope.hidden, $scope.linked, $scope.spam);

      $scope.isLoading = true;
      newsService.getNews($scope.hidden, $scope.linked, $scope.spam, offset, $scope.newsFilter).then(function(data){
        console.log("Got some news");
        $scope.isLoading = false;
        $scope.newsArticles = data.articles;
        newsVm.total_count = data.total_count;
        $scope.maxOffset = Math.min(offset+10, newsVm.total_count);
      });
    }



  }

})();
