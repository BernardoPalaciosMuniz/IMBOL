close all;

[D,t]=spread(IS(:,:,:),yR,Ddpix,fps,imscale);

function [d,t]=spread(IS,yR,D,fps,imscale)
    FG=min(IS,[],3);
    
    
    BW=~imbinarize(FG);
    BW = bwareaopen(BW,50);
    BW=imfill(BW,'holes');
    
    BW(yR:end,:,:)=0;
    BW=bwareafilt(BW,1);
    
  
    
    skel=bwskel(BW,'MinBranchLength',10);
    
%     imshow(skel,[])
    [y,x]=find(skel);
    x1=x(x==min(x));
    x2=x(x==max(x));
    y1=y(x==min(x));
    y2=y(x==max(x));
    c=size(IS,3);
    d=zeros(c,1);
    BG=max(IS,[],3);
    dnow=D*1.5;
%     imshow(BG,[])
    
    
    


    while dnow>=D*1.1
        FG=imsubtract(BG,IS(:,:,c));
        halfwidth=30;
        roi=FG(y1-halfwidth:y2+halfwidth,x1-halfwidth:x2+halfwidth);
        BW=imbinarize(roi);
        BW = bwareaopen(BW,150);
        BW=imfill(BW,'holes');
        [y,x]=find(BW);
        xf=max(x);
        x0=min(x);
        if dnow>=D*1.5
            yf=mean(y(x==xf));
            y0=mean(y(x==x0));
        end
        dnow=sqrt((xf-x0)^2+(yf-y0)^2);
        if(dnow>=D*1.1)
            d(c,1)=dnow;
            imshow(BW,[])
            hold on
            plot([x0,xf],[y0,yf])
            hold off
            drawnow
            c=c-1;
        end
 


    end


     d=d(c+1:end,1)*imscale;
     t=(0:length(d)-1)/fps;
     t=t';
     
        
    
    
    
    

end

