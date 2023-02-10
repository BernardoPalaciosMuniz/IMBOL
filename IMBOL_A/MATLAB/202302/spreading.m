% close all;


D_f=spread(IS_f,impactframe,endframe,imscale_f);

function D=spread(IS,impactframe,endframe,imscale)
    BG=uint16(median(IS(:,:,1:100),3));
    nf=endframe-impactframe+1;
    D=zeros(nf,1);
    figure
    for i=1:nf
        I=IS(:,:,end-nf+i);
%         imshow(I,[])
        FG=imabsdiff(I,BG);
%         imshow(FG,[])
        BW=FG>0.07*2^12;
        BW=bwareaopen(BW,200);
        BW=bwmorph(BW,'open');
        
        BW=imfill(BW,'holes');
        BW=bwmorph(BW,'remove');
        [~,c]=find(BW);
        
%         imshow(BW,[])
%         BW=bwskel(BW,'MinBranchLength',10);
%         BW=bwskel(BW);
%         BW=bwmorph(BW,'thin',Inf);       
%          imshow(I,[])
%          hold on
%          plot(min(c),r(c==min(c)),'*')
%          plot(max(c),r(c==max(c)),'*')
%          hold off
%          axis([400 700 600 1000])
%          drawnow
         D(i)=max(c)-min(c);

        
    end
     D=D*imscale;
     
     plot(smooth(D))
     drawnow


     
        
    
    
    
    

end

