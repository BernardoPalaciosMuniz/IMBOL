close all;
filename=imfiles(1);
info = imfinfo(filename);
nI = length(info);
[rows,cols]=size(imread(filename, 1));
IS=zeros([rows,cols,nI],'uint8');
BS=zeros([rows,cols,nI],'uint8');
BWS=zeros([rows,cols,nI],'logical');
R=zeros([nI 1],'double');
THETA=zeros([nI 1],'double');
AR=zeros([nI 1],'double');
X=zeros([nI 2],'double');
Y=zeros([nI 1],'double');



for k = 1 : nI
    
    Ic = imread(filename, k);
    IS(:,:,k) = Ic;
    BS(:,:,k)=imabsdiff(IS(:,:,k),IS(:,:,1));
    
end

 figure;
 X0=[0 0];
for k = 1 : nI
    I=BS(:,:,k);
    I(I<10)=0;
    BW=imbinarize(I);
    BW = bwareaopen(BW,10);
    BW=[ones(1,cols,'logical');BW];
    BW=imfill(BW,'holes');
    BW(1,:)=[];
    BWS(:,:,k)=BW;
    BWstats=regionprops(BW,'MajorAxisLength','MinorAxisLength',"Centroid","Orientation");
    if ~isempty(BWstats)
        [M,i]=max([BWstats.MajorAxisLength]);
        r=BWstats(i).MajorAxisLength/2;
        AR(k)=BWstats(i).MajorAxisLength/BWstats(i).MinorAxisLength;
        theta0=deg2rad(BWstats(i).Orientation);
        x0=BWstats(i).Centroid;
        x=x0(1)+(r*[-cos(theta0),cos(theta0)]);
        y=x0(2)+(r*[sin(theta0),-sin(theta0)]);
        [cx,cy,c] =improfile(BW,x,y,1000);
        i0=find(c,1);
        in=find(c,1,"last");
        R(k)=sqrt((cx(in)-cx(i0))^2+(cy(in)-cy(i0))^2)/2;
        THETA(k)=theta0;
        if X0==[0,0]
            X0=x0;
        end
        Y(k)=norm(x0-X0);
        X(k,:)=x0;
        
        imshow(IS(:,:,k))
        hold on;
        plot([cx(i0),cx(in)],[cy(i0),cy(in)],'r-');
        hold off
        drawnow
    else
        R(k)=NaN;
        THETA(k)=NaN;
        Y(k)=NaN;
        X(k,:)=[NaN NaN];
    end
end


t0=find(Y>R+5,1);
% timpact=find(abs(THETA)>pi/3,1);
timpact=find([0;abs(diff(R))]>5&(1:nI)'>t0,1);
f=(stdfilt(Y)<0.05&(1:nI)'>t0);
xsurf=mean(X(f,1));
ysurf=mean(X(f,2));
rmax=max(R)+10;
THETAsurf=mean(THETA(f));

for k = t0:nI
    BW=BWS(:,:,k);
    BW(ceil(ysurf):rows,:)=[];
    BWstats=regionprops(BW,'MajorAxisLength','MinorAxisLength',"Centroid","Orientation");
    BW=BWS(:,:,k);
    [M,i]=max([BWstats.MajorAxisLength]);
    r=BWstats(i).MajorAxisLength/2;
    AR(k)=BWstats(i).MajorAxisLength/BWstats(i).MinorAxisLength;
    if k<timpact
        theta0=deg2rad(BWstats(i).Orientation);
        x0=BWstats(i).Centroid;
        x=x0(1)+(r*[-cos(theta0),cos(theta0)]);
        y=x0(2)+(r*[sin(theta0),-sin(theta0)]);
        [cx,cy,c] =improfile(BW,x,y,1000);
        
    else
        theta0=THETAsurf;
        x0=[xsurf ysurf];
        x=x0(1)+(rmax*[-cos(theta0),cos(theta0)]);
        y=x0(2)+(rmax*[sin(theta0),-sin(theta0)]);
        [cx,cy,c] =improfile(BW,x,y,1000);
    end
    c(isnan(c))=0;
    i0=find(c,1);
    in=find(c,1,"last");
    R(k)=sqrt((cx(in)-cx(i0))^2+(cy(in)-cy(i0))^2)/2;
    THETA(k)=theta0;
    Y(k)=norm(BWstats(i).Centroid-X0);
    X(k,:)=BWstats(i).Centroid;
    imshow(BWS(:,:,k))
    hold on;
    plot([cx(i0),cx(in)],[cy(i0),cy(in)],'r-');
    hold off
    drawnow
end

tfall=t0:timpact;
Rd=mean(R(tfall));



figure('Name','R(t)') ;
plot(R)
figure('Name','THETA(t)') ;
plot(THETA)
ylim([-pi/2 pi/2])
figure('Name','AR(t)') ;
plot(AR(t0:timpact))
figure('Name','Y(t)') ;
plot(Y(t0:timpact))