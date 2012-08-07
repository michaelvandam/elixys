package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Extended.Form;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This logo component is an extension of our extended Form class
	public class Logo extends Form
	{
		/***
		 * Construction
		 **/
		
		public function Logo(screen:Sprite, xml:XML, attributes:Attributes)
		{
			// Pass the visible flag
			var pXML:XML;
			if (!Styling.bSmallScreenDevice)
			{
				pXML = new XML(LOGO_FULL);
			}
			else
			{
				pXML = new XML(LOGO_SMALL);
			}
			if (xml.@visible == "true")
			{
				pXML.@visible = "true";
			}
			else if (xml.@visible == "false")
			{
				pXML.@visible = "false";
			}
			
			// Call the base constructor
			super(screen, pXML, attributes);
		}

		/***
		 * Member variables
		 **/

		// Logo component XML
		protected static const LOGO_FULL:XML = 
			<columns gapH="0" widths="24%,76%">
				<frame />
				<rows gapV="0" heights="55%,45%">
					<label useEmbedded="true" alignH="left" alignV="bottom">
						<font face="GothamLight" color={Styling.TEXT_BLACK} size="60">
							ELIXYS
						</font>
					</label>
					<columns gapH="0" widths="6,100%">
						<frame />
						<vertical gapV="0">
							<label alignH="left" alignV="top">
								<font color={Styling.TEXT_GRAY3} size="18">
									Automated Radiochemical
								</font>
							</label>
							<label alignH="left" alignV="top">
								<font color={Styling.TEXT_GRAY3} size="18">
									Synthesis Platform
								</font>
							</label>
						</vertical>
					</columns>
				</rows>
			</columns>;
		protected static const LOGO_SMALL:XML = 
			<columns gapH="0" widths="10%,90%">
				<frame />
				<rows gapV="0" heights="55%,45%">
					<label useEmbedded="true" alignH="left" alignV="bottom">
						<font face="GothamLight" color={Styling.TEXT_BLACK} size="60">
							ELIXYS
						</font>
					</label>
					<columns gapH="0" widths="6,100%">
						<frame />
						<vertical gapV="0">
							<label alignH="left" alignV="top">
								<font color={Styling.TEXT_GRAY3} size="18">
									Automated Radiochemical
								</font>
							</label>
							<label alignH="left" alignV="top">
								<font color={Styling.TEXT_GRAY3} size="18">
									Synthesis Platform
								</font>
							</label>
						</vertical>
					</columns>
				</rows>
			</columns>;
	}
}
