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
			var pXML:XML = new XML(LOGO);
			if (xml.@visible == "true")
			{
				pXML.@visible = "true";
			}
			else if (xml.@visible == "false")
			{
				pXML.@visible = "false";
			}
			
			// Call the base constructor
			super(screen, LOGO, attributes);
		}

		/***
		 * Member variables
		 **/

		// Logo component XML
		protected static const LOGO:XML = 
			<columns gapH="0" widths="15%,85%">
				<frame />
				<rows gapV="0" heights="55%,45%">
					<label useEmbedded="true" alignH="left" alignV="bottom">
						<font face="GothamLight" color={Styling.TEXT_GRAY} size="64">
							ELIXYS
						</font>
					</label>
					<columns gapH="0" widths="6,100%">
						<frame />
						<label alignH="left" alignV="top">
							<font color={Styling.TEXT_GRAY} size="16">
								Automated Radiochemical Synthesis Platform
							</font>
						</label>
					</columns>
				</rows>
			</columns>
	}
}
