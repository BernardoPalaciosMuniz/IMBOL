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
    
    results=readtable(file);
    Dmax=results{:,'Dmaxf_m'};
    Dd=results{:,'Dd_m'};
    Dnorm=Dmax./Dd;
    We=results{:,'We'};
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
