close all;
[U,Dd,Ddpix,Umin]=getBG(IS,yU,fps,imscale);


function [U,D,Dpix,Umin]=getBG(IS,yU,fps,imscale)
    BG=uint16(mean(IS,3));
    x=zeros(size(IS,3),1);
    y=x;
    c=0;
    D=0;
    while y<yU-20
        c=c+1;
        FG=imsubtract(BG,IS(:,:,c));
        BW=imbinarize(FG);
        BW = bwareaopen(BW,10);
        BW=imfill(BW,'holes');
        BW=BW(1:yU+10,:);
        BWstats=regionprops(BW,'MajorAxisLength','MinorAxisLength',"Centroid");
        [~,i]=max([BWstats.MajorAxisLength]);
        x0=BWstats(i).Centroid;
        x(c)=x0(1);
        y(c)=x0(2);
        A=BWstats(i).MajorAxisLength;
        a=BWstats(i).MinorAxisLength;
        D=D+(a+A)/2;
    end
    x=x(1:c,1);
    y=y(1:c,1);
    D=D/c;
    Dpix=D;
    mask=y<(yU-2*D);
    u=smooth(sqrt(diff(y).^2+diff(x).^2),6);
    u=u(mask);
    U=u(end);
    for c=1:length(x)
        imshow(IS(:,:,c),[])
        hold on
        viscircles([x(c),y(c)],D/2);
        hold off
        drawnow
    end
    
    plot(smooth(sqrt(diff(y).^2+diff(x).^2),6))
    hold on
    plot(ones(length(x),1)*U)
    hold off
    drawnow
    D=D*imscale;
    U=U*imscale*fps;
    Umin=min(u)*imscale*fps;


end
