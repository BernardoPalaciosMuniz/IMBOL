close all
folder='20220915';
[We,Dnorm,files]=makeplots(folder);
function [We,Dnorm,files]=makeplots(folder)
    files=dir([folder,'/*We_Rmax.csv']);
    PTfile=dir([folder,'/exp_log*.csv']);
    PTfile=[PTfile(1).folder,'/',PTfile(1).name];
    PT=readmatrix(PTfile);
    P=PT(:,1);
    Tsurf=PT(:,2);
    Tres=PT(:,3);
    cp=1300;
    hfg=142;
    Jk=cp*(Tsurf-Tres)/hfg;
    file=[files(1).folder,'/',files(1).name];
    nrows=length(files);
    ncols=size(readmatrix(file),2);
    WeRmax=zeros(nrows,ncols);
    for n=1:nrows
        file=[files(n).folder,'/',files(n).name];
    WeRmax(n,:)=readmatrix(file);
    end
    Dd=WeRmax(:,1);
    U=WeRmax(:,2);
    We=WeRmax(:,3);
    Dmax=WeRmax(:,4);
    Dnorm=Dmax./Dd;
    loglog(Jk,Dnorm,'*b')
    files=dir([folder,'/*Rvst.csv']);
    nfiles=length(files);
    nframes=80;
    figure
    ax1=axes;

    for n=1:nfiles
        file=[files(n).folder,'/',files(n).name];
        Rvst=readmatrix(file);
        Rvst=Rvst(1:nframes,:);
        t=Rvst(:,1);
        D=Rvst(:,2);
        jk=ones(length(t),1)*Jk(n);
        scatter(ax1,t,D,[],jk)

        if n==1
            hold([ax1 ], 'on')
        end
        
    end
    hold off
    set([ax1],'xscale','log','yscale','log')
    colorbar(ax1)
    
    
    
    
    
end