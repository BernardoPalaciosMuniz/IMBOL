close all;
[U,Dd,Ddpix]=getBG(IS_f,startframe,impactframe,fps,imscale_f);


function [U,D,Dpix]=getBG(IS,startframe,impactframe,fps,imscale)

if impactframe-startframe<130
    nf=45;
elseif impactframe-startframe<170
    nf=120;
else
    nf=150;
end
BG=IS(:,:,1:impactframe-startframe);
BG=uint16(median(BG,3));
    x=zeros(nf,1);
    y=x;
    D=x;
%     R=[10 35];
    for c=1:nf
        i=c+impactframe-startframe-nf;
        FG=imabsdiff(BG,IS(:,:,i));
%         imshow(FG,[0 2^12])
        BW=imbinarize(FG);
        BW = bwareaopen(BW,50);
        BW=imfill(BW,'holes');
        
%         BWstats=regionprops(BW,'MajorAxisLength','MinorAxisLength',"Centroid");
%         [~,i]=max([BWstats.MajorAxisLength]);
%     
%         x0=BWstats(i).Centroid;
%         x(c)=x0(1);
%         y(c)=x0(2);
%         A=BWstats(i).MajorAxisLength;
%         a=BWstats(i).MinorAxisLength;
%         D=D+(a+A)/2;

%         [centers,radii]=imfindcircles(BW,R,'Sensitivity',0.95);
        
        stats = regionprops('table',BW,'Centroid','MajorAxisLength','MinorAxisLength');
        centers = stats.Centroid;
        diameters = mean([stats.MajorAxisLength stats.MinorAxisLength],2);
        radii = diameters/2;
        if ~isempty(radii)
            if  c==1
                x(c)=centers(radii==max(radii),1);
                y(c)=centers(radii==max(radii),2);
                r=max(radii);
            
            else
                xnow=centers(:,1);
                ynow=centers(:,2);
                dx=xnow-x(c-1);
                dy=ynow-y(c-1);
                delta=sqrt(dy.^2+dx.^2);
                x(c)=centers(delta==min(delta),1);
                y(c)=centers(delta==min(delta),2);
                r=max(radii);
            end
            
                
            D(c)=2*r;
%             r=round(r);
%             R=[-8 8]+r;
%             imshow(FG,[])
%             hold on
%             viscircles([x(c),y(c)],D(c)/2);
%             hold off
%             drawnow
        end
        
        
    end
%     c=1;
%     while y(c)
    

    D=mean(D);
    Dpix=D;

    u=sqrt(diff(y).^2+diff(x).^2);
    X=sqrt((y-y(1)).^2+(x-x(1)).^2);
    
    
    freefallfit = fittype('g/2*x.^2+a*x+b','problem','g');

    t=1:length(x);
    t=t';
    g=(9.81/(fps^2*imscale));
    fitout = fit(t,X,freefallfit,'StartPoint',[mean(u) X(1)],'problem',g);

    U=coeffvalues(fitout);
    U=U(1)+g*(t(end));
%     for c=1:length(x)
%         i=c+impactframe-startframe-nf;
%         imshow(IS(:,:,i),[])
%         hold on
%         viscircles([x(c),y(c)],D/2);
%         hold off
%         drawnow
%     end

%     fy=fit(1:nI,y,'poly1');
    

   
    plot(X)
    hold on
    plot(fitout)
    hold off
    drawnow
    mean(U)
    fit(t,X,'poly1')
    U
    D=D*imscale;
    U=U*imscale*fps;


end
