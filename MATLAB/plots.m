close all
folder='20220914';
[We,Dnorm,files]=makeplots(folder);
function [We,Dnorm,files]=makeplots(folder)
    cond='N7000_N7000';
    files=dir([folder,strcat('/',cond,'*We_Rmax.csv')]);
    file=[files(1).folder,'/',files(1).name];
    nrows=length(files);
    ncols=size(readmatrix(file),2);
    WeRmax=zeros(nrows,ncols);
    for n=1:nrows
        file=[files(n).folder,'/',files(n).name];
    WeRmax(n,:)=readmatrix(file);
    end
    Dd=WeRmax(:,1);
    We=WeRmax(:,3);
    Dmax=WeRmax(:,4);
    Dnorm=Dmax./Dd;
    loglog(We,Dnorm,'*b')
    hold on
    plot(We,2.5*We.^0.12)
    hold off
    files=dir([folder,strcat('/',cond,'*Rvst.csv')]);
    nfiles=length(files);
    nframes=100;
    figure
    ax1=axes;
    figure
    ax2=axes;
    for n=1:nfiles
        file=[files(n).folder,'/',files(n).name];
        Rvst=readmatrix(file);
        if nframes>length(Rvst)
            nframes=length(Rvst);
        end
        Rvst=Rvst(1:nframes,:);
        t=Rvst(:,1);
        D=Rvst(:,2);
        we=ones(length(t),1)*We(n);
        tnorm=t*we(1)^(0.5);
        dnorm=D/Dd(n);
        scatter(ax1,t,D,[],we)
        scatter(ax2,tnorm,dnorm,[],we)
        if n==1
            hold([ax1 ax2], 'on')
        end
        
    end
    
    plot(ax2,logspace(-3,-1),8*logspace(-3,-1).^0.3)
    hold off
    set([ax1,ax2],'xscale','log','yscale','log')
    colorbar(ax1)
    colorbar(ax2)
    
    
    
    
    
end