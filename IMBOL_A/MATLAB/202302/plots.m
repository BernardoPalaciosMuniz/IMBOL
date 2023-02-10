legends_2211=plotall('Results_2211.csv');
hold on
legends_2209=plotall('Results_2209.csv');
legends=[legends_2211,legends_2209];
legend(legends);
x=1e1:1e3;
hold on
plot(x,1.3*x.^(1/4))
plot(x,2*x.^(1/8))
hold off
function legends=plotall(file)
%     rho=1400;%N7000
%     sigma=12.4e-3;%N7000
%     hfg=142e03;%N7000
%     cp=1300;%N7000
%     rho=789;%Ethanol density
%     gamma=23.1;%Ethanol surface tension
%     hfg=839;% Ethanol heat of vaporization
%     cp=2420;%Ethanol hat capacity at 25 C
%     mu=1.17e-3;%Ethanol viscosity 
    
    results=readtable(file);
    Dmax=results{:,'Dmaxf_m'};
    Dd=results{:,'Dd_m'};
    Dnorm=Dmax./Dd;
    We=results{:,'We'};

%     
%     We=rho*U^2*Dd/gamma;
%     Ja=cp*(T_surfC-T_resC)/hfg;
%     Re=rho*U*Dd/mu;
    date=results{:,'sourcef'};
    date=extractBefore(date,'__');
    date=string(date);
    datecat=unique(date);
    legends=cell(1,length(datecat));
    for i=1:length(datecat)
       filt=date==datecat(i);
       loglog(We(filt),Dnorm(filt),'*')
       legends{i}=datecat(i);
       hold on
       
    end
    hold off
    
     axis([1e1 1e3 1e0 1e1])
     legend(legends)
    
end
