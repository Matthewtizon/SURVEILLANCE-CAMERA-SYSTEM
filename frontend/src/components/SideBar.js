// src/components/Sidebar.js
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import VideocamIcon from '@mui/icons-material/Videocam';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary'; // Import icon for recorded video
import PersonAddIcon from '@mui/icons-material/PersonAdd'; // Import icon for add person page
import { styled } from '@mui/system';

const drawerWidth = 240;

const openedMixin = (theme) => ({
    width: drawerWidth,
    transition: theme.transitions.create('width', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
    }),
    overflowX: 'hidden',
});

const closedMixin = (theme) => ({
    transition: theme.transitions.create('width', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
    }),
    overflowX: 'hidden',
    width: `calc(${theme.spacing(7)} + 1px)`,
    [theme.breakpoints.up('sm')]: {
        width: `calc(${theme.spacing(9)} + 1px)`,
    },
});

const DrawerHeader = styled('div')(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: theme.spacing(0, 1),
    ...(theme.mixins && theme.mixins.toolbar ? theme.mixins.toolbar : {}),
}));

const CustomDrawer = styled(Drawer, { shouldForwardProp: (prop) => prop !== 'open' })(
    ({ theme, open }) => ({
        width: drawerWidth,
        flexShrink: 0,
        whiteSpace: 'nowrap',
        boxSizing: 'border-box',
        ...(open && {
            ...openedMixin(theme),
            '& .MuiDrawer-paper': openedMixin(theme),
        }),
        ...(!open && {
            ...closedMixin(theme),
            '& .MuiDrawer-paper': closedMixin(theme),
        }),
    })
);

const Sidebar = ({ isOpen, toggleSidebar, role }) => {
    const theme = useTheme();
    const navigate = useNavigate();

    const handleDashboardClick = () => {
        if (role === 'Administrator') {
            navigate('/admin-dashboard');
        } else if (role === 'Security Staff') {
            navigate('/security-dashboard');
        }
    };

    return (
        <CustomDrawer variant="permanent" open={isOpen} theme={theme}>
            <DrawerHeader>
                <IconButton onClick={toggleSidebar}>
                    <MenuIcon />
                </IconButton>
            </DrawerHeader>
            <List>
                <ListItem button onClick={handleDashboardClick}>
                    <ListItemIcon>
                        <DashboardIcon />
                    </ListItemIcon>
                    {isOpen && <ListItemText primary="Dashboard" />}
                </ListItem>
                <ListItem button component={Link} to="/user-management">
                    <ListItemIcon>
                        <PeopleIcon />
                    </ListItemIcon>
                    {isOpen && <ListItemText primary="User Management" />}
                </ListItem>
                <ListItem button component={Link} to="/camera-stream">
                    <ListItemIcon>
                        <VideocamIcon />
                    </ListItemIcon>
                    {isOpen && <ListItemText primary="Camera Stream" />}
                </ListItem>
                <ListItem button component={Link} to="/recorded-videos">
                    <ListItemIcon>
                        <VideoLibraryIcon />
                    </ListItemIcon>
                    {isOpen && <ListItemText primary="Recorded Videos" />}
                </ListItem>
                {/* Add Person Item */}
                <ListItem button component={Link} to="/add-person">
                    <ListItemIcon>
                        <PersonAddIcon /> {/* Icon for adding person */}
                    </ListItemIcon>
                    {isOpen && <ListItemText primary="Add Person" />}
                </ListItem>
            </List>
        </CustomDrawer>
    );
};

export default Sidebar;
