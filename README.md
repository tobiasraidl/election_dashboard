### TODOs

[ ] Implement graph tweaker settings
    [x] Slider for min same shared images to show edges
    [x] Party selection checklist
        [x] Color map party selection checklist
    [x] Boolean selector to highlight edges of accounts with different party affiliation that posted the same image or the nodes directly that have adjacent diff party nodes
    [x] (maybe) Selector for num of iterations for layout generation (for faster load time)

[x] On node click open account info on sidebar below the graph filter settings
    [x] Num images posted by account, Hash shared same imagse as account with different party affiliation: yes/no,
    [ ] Better attention color

[ ] On edge click show images that both accounts posted on sidebar or modal (choose)
    [ ] On image click of edge details show image details as in platform view
        [ ] Make this a function in helper.py and nice popup so that it can be used in both pages
    [ ] Add alert that this is a cross party connection
    [ ] 

[x] Load initial graph elements from json instead of calculating it on demand

[x] Improve performance by using an "Apply" button

<!-- [ ] Custom function to map node size to either degree or num of posts (mby boolean setting for user to choose) -->

[x] Fix bug where some edges dont contain at least min same images shared that are selected

##### Platform finish
[ ] Ideate and experiment if network graph would make sense or keep it like it is
[ ]