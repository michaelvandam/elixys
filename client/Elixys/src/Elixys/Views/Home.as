package Elixys.Views
{
	import Elixys.Assets.Styling;
	import Elixys.Components.*;
	import Elixys.Events.*;
	import Elixys.Extended.*;
	import Elixys.JSON.Post.PostHome;
	import Elixys.JSON.State.State;
	import Elixys.JSON.State.StateHome;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.utils.*;
	
	// This home view is an extension of our extended Screen class
	public class Home extends Screen
	{
		/***
		 * Construction
		 **/
		
		public function Home(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			var pXML:XML;
			if (!Styling.bSmallScreenDevice)
			{
				pXML = HOME_FULLSCREEN;
			}
			else
			{
				pXML = HOME_SMALLSCREEN;
			}
			super(screen, pElixys, pXML, attributes, row, inGroup);
		}

		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public override function LoadNext():Boolean
		{
			if (m_nChildrenLoaded < LOAD_STEPS)
			{
				// Step 1 is loading the navigation bar
				if (m_nChildrenLoaded == 0)
				{
					LoadNavigationBar();
				}
				
				// Step 2 is loading the logo
				if (m_nChildrenLoaded == 1)
				{
					if (!Styling.bSmallScreenDevice)
					{
						LoadLogo();
					}
				}
				
				// Increment and return
				++m_nChildrenLoaded;
				return true;
			}
			else
			{
				// Load complete
				return false;
			}
		}

		// Load the navigation bar
		protected function LoadNavigationBar():void
		{
			// Get the navigation bar container
			var pContainer:Form = Form(findViewById("home_navigationbar_container"));
			
			// Load the navigation bar
			var pAttributes:Attributes = new Attributes(0, 0, width, height);
			var pXML:XML;
			if (!Styling.bSmallScreenDevice)
			{
				pXML = NAVIGATION_FULLSCREEN;
			}
			else
			{
				pXML = NAVIGATION_SMALLSCREEN;
			}
			m_pNavigationBar = new NavigationBar(pContainer, pXML, pAttributes);
			m_pNavigationBar.addEventListener(ButtonEvent.CLICK, OnButtonClick);
			
			// Append the navigation bar to the XML and refresh
			pContainer.xml.appendChild(pXML);
			pContainer.AppendChild(m_pNavigationBar);
			layout(attributes);
		}

		// Load the logo
		protected function LoadLogo():void
		{
			// Get the logo container
			var pContainer:Form = Form(findViewById("home_logo_container"));
			
			// Load the logo
			var pAttributes:Attributes = new Attributes(0, m_pNavigationBar.height, width, height);
			m_pLogo = new Logo(pContainer, LOGO, pAttributes);

			// Append the logo to the XML and refresh
			pContainer.xml.appendChild(LOGO);
			pContainer.AppendChild(m_pLogo);
			layout(attributes);
		}

		/***
		 * Member functions
		 **/
		
		// Updates the state
		public override function UpdateState(pState:State):void
		{
			// Update the navigation bar buttons
			var pStateHome:StateHome = new StateHome(null, pState);
			m_pNavigationBar.UpdateButtons(pStateHome.Buttons);
		}

		// Called when a button on the navigation bar is clicked
		protected function OnButtonClick(event:ButtonEvent):void
		{
			// Handle the log out button
			if (event.button == "LOGOUT")
			{
				m_pElixys.dispatchEvent(new Event(ElixysEvents.LOGOUT));
				return;
			}
			
			// Send the button click to the server
			var pPostHome:PostHome = new PostHome();
			pPostHome.TargetID = event.button;
			DoPost(pPostHome, "HOME");
		}

		/***
		 * Member variables
		 **/

		// Home screen XML
		protected static const HOME_FULLSCREEN:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows gapV="0" border="false" heights="18%,64%" alignH="fill" alignV="fill">
					<frame id="home_navigationbar_container" alignV="fill" alignH="fill" />
					<columns id="home_logo_container" gapH="0" widths="34%,66%" alignH="fill" alignV="fill" />
				</rows>
			</frame>;
		protected static const HOME_SMALLSCREEN:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows gapV="0" border="false" heights="18%,82%" alignH="fill" alignV="fill">
					<frame id="home_navigationbar_container" alignV="fill" alignH="fill" />
					<label useEmbedded="true" alignH="centre" alignV="centre">
						<font face="GothamMedium" color={Styling.TEXT_BLACK} size="24">
							System is idle.
						</font>
					</label>
				</rows>
			</frame>;

		// Navigation bar XML
		protected static const NAVIGATION_FULLSCREEN:XML =
			<navigationbar alignH="fill" alignV="fill" skin={getQualifiedClassName(navigationBar_mc)} verticaloffset="-11">
				<navigationbaroption name="SEQUENCER" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY4}
						foregroundskinup={getQualifiedClassName(mainNav_sequencer_up)}
						foregroundskindown={getQualifiedClassName(mainNav_sequencer_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_sequencer_disabled)}>
					SEQUENCER
				</navigationbaroption>
				<navigationbaroption name="MYACCOUNT" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY4}
						foregroundskinup={getQualifiedClassName(mainNav_myAccount_up)}
						foregroundskindown={getQualifiedClassName(mainNav_myAccount_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_myAccount_disabled)}>
					MY ACCOUNT
				</navigationbaroption>
				<navigationbaroption name="MANAGEUSERS" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY4}
						foregroundskinup={getQualifiedClassName(mainNav_manageUsers_up)}
						foregroundskindown={getQualifiedClassName(mainNav_manageUsers_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_manageUsers_disabled)}>
					MANAGE USERS
				</navigationbaroption>
				<navigationbaroption name="VIEWLOGS" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY4}
						foregroundskinup={getQualifiedClassName(mainNav_exportData_up)}
						foregroundskindown={getQualifiedClassName(mainNav_exportData_down)}
						foregroundskindisabled={getQualifiedClassName(mainNav_exportData_disabled)}>
					VIEW LOGS
				</navigationbaroption>
				<navigationbaroption name="VIEWRUN" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY4}
						foregroundskinup={getQualifiedClassName(mainNav_activeRun_up)}
						foregroundskindown={getQualifiedClassName(mainNav_activeRun_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_activeRun_disabled)}>
					VIEW ACTIVE RUN
				</navigationbaroption>
				<navigationbaroption name="LOGOUT" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY4}
						foregroundskinup={getQualifiedClassName(mainNav_logOut_up)}
						foregroundskindown={getQualifiedClassName(mainNav_logOut_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_logOut_disabled)}>
					LOG OUT
				</navigationbaroption>
			</navigationbar>;
		protected static const NAVIGATION_SMALLSCREEN:XML =
			<navigationbar alignH="fill" alignV="fill" skin={getQualifiedClassName(navigationBar_mc)} verticaloffset="-6">
				<navigationbaroption name="LOGOUT" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY4}
						foregroundskinup={getQualifiedClassName(mainNav_logOut_up)}
						foregroundskindown={getQualifiedClassName(mainNav_logOut_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_logOut_disabled)}>
					LOG OUT
				</navigationbaroption>
			</navigationbar>;

		// Logo XML
		protected static const LOGO:XML =
			<logo id="Logo" />;
		
		// Number of steps required to load this object
		public static var LOAD_STEPS:uint = 2;
		
		// The current step
		protected var m_nChildrenLoaded:uint = 0;

		// Screen components
		protected var m_pNavigationBar:NavigationBar;
		protected var m_pLogo:Logo;
	}
}
