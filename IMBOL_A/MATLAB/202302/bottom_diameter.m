% close all;
D_b=getD(IS_b,BG_b,imscale_b,Dd);



function D=getD(IS,BG,imscale,Dd)

    BGmean=uint16(mean(BG,3));
    BGmean=imgaussfilt(BGmean);
    x=zeros(size(IS,3),1);
    y=x;
    D=x;
    nI=size(IS,3);
%     frames=struct('cdata', cell(1,nI), 'colormap', cell(1,nI));
%     R=[80 140];
    
    for  c=1:nI
        FG=IS(:,:,c);
        FG=imgaussfilt(FG);
        FG=imabsdiff(BGmean,FG);
%         imshow(FG,[]);
        
%         Adjust threshold
        FG=FG>0.03*2^12;
        
        
        FG=bwareaopen(FG,50);
%         imshow(FG,[]);
        
        CH=bwconvhull(FG);
        CH=bwmorph(CH,'remove');
        CH=bwmorph(CH,'thicken',3);
        FG=FG & CH;
        [yy,xx]=find(FG);
        if c<40
            [x(c),y(c),R] = circfit(xx,yy);
            D(c)=2*R;
        else
            if c==40
                xmean=mean(x(1:39));
                ymean=mean(y(1:39));
            end
%             x(c)=xmean;
%             y(c)=ymean;
            rr= sqrt((xx-xmean).^2+(yy-ymean).^2);
%             if c==3
%                 [f,xi] = ksdensity(rr);
%                 plot(xi,f);
%                 pause(5);
%             end
%             rfilt=0.8*D(c-1)/2;
%             [~,E]=discretize(rr,2)
            
            [f,ri] = ksdensity(rr);
            [~,Ir]=max(f);
            rfilt=ri(Ir);
            rfilt=0.8*rfilt;
            xx=xx(rr>rfilt);
            yy=yy(rr>rfilt);
            [x(c),y(c),R] = circfit(xx,yy);
            D(c)=2*R;
        end
            
        
%         stats = regionprops('table',FG,'Centroid','MajorAxisLength','MinorAxisLength');
%         centers = stats.Centroid;
%         diameters = mean([stats.MajorAxisLength stats.MinorAxisLength],2);
%         radii = diameters/2;
        


        
        

%         [centers,radii]=imfindcircles(FG,R,'Sensitivity',0.97);


%         if ~isempty(radii)
%             x(c)=centers(radii==max(radii),1);
%             y(c)=centers(radii==max(radii),2);
%             D(c)=2*max(radii);
%             
%             if c==nI
%                 r=round(max(radii));
%             else
%                 r=2*round(max(radii))-r;
%             end
%             R=[-7 7]+r;
%         end




%         hold on
%         viscircles([x(c),y(c)],D(c)/2,'LineStyle',':','EnhanceVisibility',false,'LineWidth',1);
%         hold off
%         drawnow
%         frames(c)=getframe;
            
    end
%     implay(frames)
%     x=x(1:c,1);
%     y=y(1:c,1);
%     D=D/c;
    

%     for c=1:length(x)
%         imshow(IS(:,:,c),[0,2^12])
%         hold on
%         viscircles([x(c),y(c)],D(c)/2,'LineStyle',':','EnhanceVisibility',false);
%         hold off
%         drawnow
%         frames(c)=getframe;
%     end
% 
    D=D*imscale;
    D(1)=Dd;
    hold on
    plot(D)
    drawnow
    hold off
    
%     t=1:length(D);
%     t=t(D);
%     
%     hold on
%     plot(t,smooth(D(D)))
%     hold off
%     implay(frames)
end


function   [xc,yc,R,a] = circfit(x,y)
%
%   [xc yx R] = circfit(x,y)
%
%   fits a circle  in x,y plane in a more accurate
%   (less prone to ill condition )
%  procedure than circfit2 but using more memory
%  x,y are column vector where (x(i),y(i)) is a measured point
%
%  result is center point (yc,xc) and radius R
%  an optional output is the vector of coeficient a
% describing the circle's equation
%
%   x^2+y^2+a(1)*x+a(2)*y+a(3)=0
%
%  By:  Izhak bucher 25/oct /1991, 
    x=x(:); y=y(:);
   a=[x y ones(size(x))]\[-(x.^2+y.^2)];
   xc = -.5*a(1);
   yc = -.5*a(2);
   R  =  sqrt((a(1)^2+a(2)^2)/4-a(3));
end

